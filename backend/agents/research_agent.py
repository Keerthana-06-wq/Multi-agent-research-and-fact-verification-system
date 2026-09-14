import json
import logging
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import wikipedia
from ddgs import DDGS

from backend.core.models import SourceItem, SourceTier
from backend.core.source_ranker import analyze_source_credibility
from backend.config import settings

logger = logging.getLogger(__name__)

# Set legitimate User-Agent required by Wikipedia API to prevent 403 Forbidden / JSON errors
try:
    wikipedia.set_user_agent("VeritasFactChecker/2.0 (https://veritas.edu; factcheck@veritas.edu)")
except Exception as e:
    logger.warning(f"Could not set Wikipedia User-Agent: {e}")

class ResearchAgent1Supporting:
    """
    Research Agent 1: Primary & Supporting Evidence Agent
    Specializes in authoritative encyclopedic archives (Wikipedia) and verified institutional benchmarks.
    Responsible for retrieving definitions, historical facts, and primary ground truth.
    """

    def __init__(self, benchmark_facts: Optional[List[Dict[str, Any]]] = None):
        self.benchmark_facts = benchmark_facts or []

    def extract_key_entities(self, text: str) -> List[str]:
        clean = re.sub(r'\b(is|are|was|were|the|a|an|in|on|at|not|does|did|will|can|all|every)\b', '', text, flags=re.IGNORECASE)
        words = [w.strip() for w in re.findall(r'\b[A-Za-z0-9-]{3,}\b', clean)]
        entities = []
        if len(words) >= 2:
            entities.append(" ".join(words[:2]))
        if words:
            entities.append(words[0])
        return entities

    def search_wikipedia(self, query: str, limit: int = 2) -> List[SourceItem]:
        sources = []
        try:
            search_queries = [query]
            entities = self.extract_key_entities(query)
            for ent in entities:
                if ent.lower() not in [q.lower() for q in search_queries]:
                    search_queries.append(ent)

            seen_titles = set()
            for sq in search_queries[:2]:
                try:
                    search_results = wikipedia.search(sq, results=limit)
                    for title in search_results:
                        if title.lower() in seen_titles:
                            continue
                        seen_titles.add(title.lower())
                        try:
                            page = wikipedia.page(title, auto_suggest=False)
                            summary = page.summary
                            snippet = summary[:450] + "..." if len(summary) > 450 else summary
                            tier, score, domain = analyze_source_credibility(page.url, page.title)
                            sources.append(SourceItem(
                                title=f"Wikipedia: {page.title}",
                                url=page.url,
                                domain=domain,
                                snippet=snippet,
                                tier=tier,
                                credibility_score=score
                            ))
                            if len(sources) >= 3:
                                break
                        except Exception:
                            continue
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"Wikipedia search warning: {e}")

        return sources

    def execute_task(self, query: str) -> List[SourceItem]:
        logger.info(f"Research Agent 1 executing supporting research task: '{query}'")
        return self.search_wikipedia(query, limit=2)


class ResearchAgent2Alternative:
    """
    Research Agent 2: Alternative & Counter-Evidence Agent
    Specializes in live web search (DuckDuckGo `ddgs`) to gather independent, contemporary,
    or contrasting evidence to avoid single-source reliance and identify counterexamples.
    """

    def search_web_live(self, query: str, max_results: int = 4) -> List[SourceItem]:
        sources = []
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                for r in results:
                    url = r.get("href", "")
                    title = r.get("title", "")
                    body = r.get("body", "")
                    tier, score, domain = analyze_source_credibility(url, title)
                    sources.append(SourceItem(
                        title=title,
                        url=url,
                        domain=domain,
                        snippet=body,
                        tier=tier,
                        credibility_score=score
                    ))
        except Exception as e:
            logger.warning(f"Live web search warning: {e}")

        return sources

    def execute_task(self, query: str) -> List[SourceItem]:
        logger.info(f"Research Agent 2 executing alternative/counter-evidence research task: '{query}'")
        return self.search_web_live(query, max_results=3)


class ResearchAgent:
    """
    Coordinating Research Agent:
    Connects Research Agent 1 (Supporting/Wikipedia) and Research Agent 2 (Alternative/Web DDGS).
    Maintains full backward compatibility with the existing system.
    """

    def __init__(self):
        self.benchmark_facts = self._load_benchmark_facts()
        self.agent_1 = ResearchAgent1Supporting(self.benchmark_facts)
        self.agent_2 = ResearchAgent2Alternative()

    def _load_benchmark_facts(self) -> List[Dict[str, Any]]:
        path = settings.BENCHMARK_DATA_PATH
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading benchmark facts: {e}")
        return []

    def check_benchmark_match(self, claim: str) -> Optional[Dict[str, Any]]:
        claim_norm = re.sub(r'[^a-zA-Z0-9\s]', '', claim).lower().strip()

        for item in self.benchmark_facts:
            exact_norm = re.sub(r'[^a-zA-Z0-9\s]', '', item.get("exact_claim_match", "")).lower().strip()
            if exact_norm == claim_norm:
                return item

        claim_clean = claim.lower().strip()
        for item in self.benchmark_facts:
            exact_norm = item.get("exact_claim_match", "").lower().strip()
            if "sun revolves around the earth" in claim_clean:
                if "sun revolves around the earth" in exact_norm:
                    return item
            elif "earth revolves around the sun" in claim_clean:
                if "earth revolves around the sun" in exact_norm:
                    return item

            keywords = item.get("keywords", [])
            if keywords and all(k in claim_clean for k in keywords):
                return item

        return None

    def gather_evidence(self, claim: str, sub_queries: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Coordinates dual research agents to collect supporting and alternative evidence.
        """
        benchmark = self.check_benchmark_match(claim)

        gathered_sources: List[SourceItem] = []
        evidence_snippets: List[str] = []

        if benchmark:
            for s in benchmark.get("sources", []):
                gathered_sources.append(SourceItem(**s))
            evidence_snippets.extend(benchmark.get("evidence", []))
            return {
                "benchmark_match": benchmark,
                "sources": gathered_sources,
                "evidence": evidence_snippets,
                "is_authoritative_benchmark": True
            }

        # 1. Research Agent 1: Wikipedia / Supporting Evidence
        q1 = sub_queries[0] if sub_queries and len(sub_queries) > 0 else claim
        wiki_sources = self.agent_1.execute_task(q1)
        gathered_sources.extend(wiki_sources)

        # 2. Research Agent 2: Live Web DDGS / Alternative Perspectives
        q2 = sub_queries[1] if sub_queries and len(sub_queries) > 1 else claim
        web_sources = self.agent_2.execute_task(q2)
        gathered_sources.extend(web_sources)

        # Deduplicate
        seen_urls = set()
        unique_sources = []
        for s in gathered_sources:
            if s.url not in seen_urls:
                seen_urls.add(s.url)
                unique_sources.append(s)

        unique_sources.sort(key=lambda s: s.credibility_score, reverse=True)

        for s in unique_sources[:5]:
            # Break snippet into full sentences
            sentences = re.split(r'(?<=[.!?])\s+', s.snippet)
            for sent in sentences:
                sent_clean = sent.strip()
                if len(sent_clean) > 20:
                    evidence_snippets.append(sent_clean)

        return {
            "benchmark_match": None,
            "sources": unique_sources[:4],
            "evidence": evidence_snippets,
            "is_authoritative_benchmark": False
        }
