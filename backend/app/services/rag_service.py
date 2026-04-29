import os
import shutil
import tempfile
from typing import Any

from fastapi import UploadFile

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.config import get_settings, KNOWLEDGE_REPO_DIR


class RagService:
    def __init__(self) -> None:
        self.settings = get_settings()
        
        # 1. Embedding Initialization
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # 2. Vector Store Initialization
        self.vector_store_dir = str(KNOWLEDGE_REPO_DIR / "vector_db")
        self.vector_store = Chroma(
            collection_name="tech_documents",
            embedding_function=self.embeddings,
            persist_directory=self.vector_store_dir
        )
        
        # Initialize LLM
        llm_kwargs: dict[str, Any] = {
            "api_key": self.settings.llm_api_key,
            "model": self.settings.llm_model,
        }
        if self.settings.llm_base_url:
            llm_kwargs["base_url"] = self.settings.llm_base_url
            
        self.llm = ChatOpenAI(**llm_kwargs)
        
        # Prompt for grounding the LLM
        self.prompt_template = ChatPromptTemplate.from_messages([
            (
                "system", 
                "You are an expert technology assistant. Answer the user's question using ONLY the provided context below. "
                "If the answer is not contained in the context, say 'I cannot find the answer in the provided documents.'\n\n"
                "Context:\n{context}"
            ),
            ("user", "{question}")
        ])

    def ingest_pdf(self, file: UploadFile) -> list[str]:
        """
        Save the uploaded file temporarily, load with PyPDFLoader,
        chunk the text, and store in the vector database.
        """
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        try:
            # Load with PyPDFLoader
            loader = PyPDFLoader(tmp_path)
            docs = loader.load()

            # Chunk the text
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                add_start_index=True
            )
            splits = text_splitter.split_documents(docs)

            # Store chunks in the vector store
            for split in splits:
                split.metadata["source_filename"] = file.filename

            doc_ids = self.vector_store.add_documents(documents=splits)
            return doc_ids
        finally:
            # Clean up the temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def ask_question(self, question: str, top_k: int = 4) -> dict[str, Any]:
        """
        Retrieve top-k relevant chunks from Chroma, construct a prompt grounding the LLM,
        and generate the answer.
        """
        # Retrieve top-k relevant chunks
        docs = self.vector_store.similarity_search(question, k=top_k)
        
        if not docs:
            return {
                "answer": "No relevant documents found in the database. Please upload a document first.",
                "sources": []
            }

        # Construct a prompt grounding the LLM strictly in the provided context
        context_text = "\n\n---\n\n".join([doc.page_content for doc in docs])
        
        prompt = self.prompt_template.invoke({
            "context": context_text,
            "question": question
        })
        
        # Generate the answer using ChatOpenAI
        response = self.llm.invoke(prompt)
        
        # Prepare and return the output including sources
        sources = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in docs
        ]
        
        return {
            "answer": str(response.content),
            "sources": sources
        }
