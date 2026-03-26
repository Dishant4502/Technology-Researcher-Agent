from __future__ import annotations

from textwrap import dedent

from crewai import Agent, Crew, LLM, Process, Task
from crewai.tools import tool

from app.config import get_settings
from app.models.schemas import SearchResult
from app.services.search import SearchService


def _format_sources(sources: list[SearchResult]) -> str:
    return "\n".join(
        f"[{index}] {source.title}\nURL: {source.url}\nSnippet: {source.snippet}\n"
        for index, source in enumerate(sources, start=1)
    )


def build_research_crew(query: str, sources: list[SearchResult], depth: str) -> Crew:
    settings = get_settings()
    llm = LLM(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        temperature=0.2,
    )
    search_service = SearchService()

    @tool("technology_web_search")
    def technology_web_search(search_query: str) -> str:
        """Search the web for current technology-industry information and return condensed findings."""
        live_results = search_service.search(search_query, limit=min(settings.research_max_sources, 5))
        return _format_sources(live_results)

    scout = Agent(
        role="Technology Research Scout",
        goal="Locate credible, current, technology-industry evidence relevant to the user's question.",
        backstory=(
            "You specialize in identifying high-signal industry news, product launches, funding activity, "
            "platform shifts, AI strategy updates, developer ecosystem moves, and competitive signals."
        ),
        llm=llm,
        tools=[technology_web_search],
        verbose=False,
        allow_delegation=False,
    )

    analyst = Agent(
        role="Technology Industry Analyst",
        goal="Synthesize research into a nuanced, decision-useful analysis with explicit citations.",
        backstory=(
            "You evaluate technology trends, execution risk, market positioning, infrastructure bets, "
            "enterprise adoption signals, and second-order implications."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    curator = Agent(
        role="Knowledge Repository Curator",
        goal="Produce a structured final report that is easy to archive and retrieve later.",
        backstory=(
            "You convert research into a precise knowledge artifact with concise summaries, key findings, "
            "actionable takeaways, and a clean source registry."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    evidence_pack = _format_sources(sources)
    depth_instruction = {
        "standard": "Keep the report concise but still cover major market signals.",
        "advanced": "Balance breadth and depth, including competitive and product implications.",
        "deep": "Include deeper strategic implications, risk factors, and emerging themes.",
    }[depth]

    map_task = Task(
        description=dedent(
            f"""
            User query: {query}

            Initial evidence pack:
            {evidence_pack}

            Use the search tool if needed to verify freshness or fill obvious gaps.
            Extract the most relevant themes, major claims, and what each source contributes.
            Focus on the technology industry. Prefer current sources and avoid speculation.
            """
        ).strip(),
        expected_output="A concise research map with bullet sections for themes, evidence, and unresolved questions.",
        agent=scout,
    )

    analysis_task = Task(
        description=dedent(
            f"""
            Transform the research map into an industry analysis for this query: {query}

            Requirements:
            - {depth_instruction}
            - Lead with the direct answer or main trend.
            - Keep the writing professional, concise, and decision-oriented.
            - Keep the overall response moderately short. Avoid filler and repeated points.
            - Include competitive, product, infrastructure, investment, or enterprise implications only when they materially matter.
            - Use bracket citations like [1], [2], [3] that map to the provided source list.
            - Flag uncertainty or conflicting evidence explicitly.
            """
        ).strip(),
        expected_output="A concise markdown analysis with sections for Executive Summary, Key Findings, Strategic Implications, and Risks.",
        agent=analyst,
        context=[map_task],
    )

    curation_task = Task(
        description=dedent(
            f"""
            Produce the final knowledge-base-ready markdown report for the query: {query}

            The report must include:
            - Title
            - Executive Summary
            - Key Findings
            - Strategic Implications
            - Open Questions
            - Sources with numbered references matching the citations

            Keep the tone analytical, polished, and professional.
            Keep each section tight. Prefer short paragraphs or compact bullets.
            In the Sources section, list only the numbered links. Do not include descriptions.
            """
        ).strip(),
        expected_output="A polished markdown report ready to store in a text-based knowledge repository.",
        agent=curator,
        context=[analysis_task],
    )

    return Crew(
        agents=[scout, analyst, curator],
        tasks=[map_task, analysis_task, curation_task],
        process=Process.sequential,
        verbose=False,
    )
