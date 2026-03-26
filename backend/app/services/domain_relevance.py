from __future__ import annotations

import re


class DomainRelevanceService:
    TECH_PHRASES = {
        "artificial intelligence",
        "machine learning",
        "deep learning",
        "large language model",
        "large language models",
        "generative ai",
        "cloud computing",
        "software engineering",
        "software development",
        "data science",
        "data engineering",
        "cyber security",
        "cybersecurity",
        "computer vision",
        "natural language processing",
        "product management",
        "digital transformation",
        "venture capital",
        "tech startup",
        "enterprise software",
        "open source",
        "semiconductor industry",
        "developer tools",
        "mobile app",
        "web development",
        "saas platform",
        "fintech platform",
        "robotics industry",
        "blockchain technology",
        "technology industry",
    }

    TECH_KEYWORDS = {
        "ai",
        "app",
        "apps",
        "api",
        "apis",
        "automation",
        "chip",
        "chips",
        "cloud",
        "code",
        "coding",
        "computer",
        "computing",
        "crypto",
        "cybersecurity",
        "data",
        "database",
        "developer",
        "developers",
        "digital",
        "fintech",
        "gpu",
        "hardware",
        "innovation",
        "internet",
        "it",
        "llm",
        "model",
        "models",
        "platform",
        "product",
        "products",
        "programming",
        "robotics",
        "saas",
        "semiconductor",
        "software",
        "startup",
        "startups",
        "system",
        "systems",
        "tech",
        "technology",
        "telecom",
        "web",
    }

    def is_technology_query(self, query: str) -> bool:
        normalized = query.strip().lower()
        if not normalized:
            return False
        if any(phrase in normalized for phrase in self.TECH_PHRASES):
            return True

        tokens = set(re.findall(r"[a-z0-9+#.-]+", normalized))
        if "it" in tokens and len(tokens) == 1:
            tokens.remove("it")

        matched_keywords = tokens.intersection(self.TECH_KEYWORDS)
        return len(matched_keywords) >= 1

    def rejection_message(self) -> str:
        return "Your query is not related to technology. Please ask a technology-focused question."
