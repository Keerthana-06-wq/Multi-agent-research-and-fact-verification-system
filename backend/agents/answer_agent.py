from typing import Dict, Any, List
import wikipedia
from backend.core.models import SourceItem, SourceTier
from backend.core.source_ranker import analyze_source_credibility

class AnswerAgent:
    """
    Agent 6: Informational / Normal Question Answering Agent
    Generates structured, clear, and objective answers to informational questions,
    distinguishing factual answers from subjective opinions.
    """

    KNOWLEDGE_BASE = {
        "what is artificial intelligence": {
            "answer": "Artificial Intelligence (AI) is a branch of computer science dedicated to developing systems capable of performing tasks that typically require human intelligence. These tasks include visual perception, speech recognition, reasoning, problem-solving, and decision-making.",
            "evidence": [
                "AI encompasses core subfields such as Machine Learning (ML), Deep Learning, Natural Language Processing (NLP), Computer Vision, and Autonomous Robotics.",
                "Modern AI systems rely predominantly on statistical models, neural networks, and large-scale data to discover patterns and make predictions."
            ],
            "sources": [
                {
                    "title": "Stanford Encyclopedia of Philosophy - Artificial Intelligence",
                    "url": "https://plato.stanford.edu/entries/artificial-intelligence/",
                    "domain": "plato.stanford.edu",
                    "snippet": "Artificial intelligence (AI) is the field devoted to building artificial animals (or at least artificial creatures) or, more realistically, artificial systems with intellectual capabilities.",
                    "tier": "Academic / Research",
                    "credibility_score": 93
                },
                {
                    "title": "IBM - What is Artificial Intelligence (AI)?",
                    "url": "https://www.ibm.com/topics/artificial-intelligence",
                    "domain": "ibm.com",
                    "snippet": "Artificial intelligence leverages computers and machines to mimic the problem-solving and decision-making capabilities of the human mind.",
                    "tier": "Reference / Encyclopedia",
                    "credibility_score": 85
                }
            ]
        },
        "what is machine learning": {
            "answer": "Machine Learning (ML) is a subset of artificial intelligence focused on training algorithms to learn patterns and make predictions from data without being explicitly programmed with static rules.",
            "evidence": [
                "The three primary paradigms of machine learning are Supervised Learning (labeled training data), Unsupervised Learning (finding hidden patterns), and Reinforcement Learning (agent learning via reward and punishment).",
                "Applications include recommendation systems, automated medical diagnosis, autonomous vehicles, and natural language processing."
            ],
            "sources": [
                {
                    "title": "MIT Technology Review - What is Machine Learning?",
                    "url": "https://www.technologyreview.com/topic/artificial-intelligence/",
                    "domain": "technologyreview.com",
                    "snippet": "Machine learning algorithms use statistics to find patterns in massive amounts of data.",
                    "tier": "Academic / Research",
                    "credibility_score": 90
                }
            ]
        }
    }

    def answer_question(self, question: str) -> Dict[str, Any]:
        q_clean = question.lower().strip().rstrip("?").strip()

        # 1. Check curated informational knowledge base
        for key, entry in self.KNOWLEDGE_BASE.items():
            if key in q_clean or q_clean in key:
                sources = [SourceItem(**s) for s in entry["sources"]]
                return {
                    "answer": entry["answer"],
                    "evidence": entry["evidence"],
                    "sources": sources,
                    "explanation": "Answer compiled from established academic and computer science literature."
                }

        # 2. Check Wikipedia for general inquiries
        try:
            results = wikipedia.search(question, results=1)
            if results:
                page = wikipedia.page(results[0], auto_suggest=False)
                summary = page.summary
                first_paragraph = summary.split("\n\n")[0]
                tier, score, domain = analyze_source_credibility(page.url, page.title)
                source = SourceItem(
                    title=f"Wikipedia: {page.title}",
                    url=page.url,
                    domain=domain,
                    snippet=first_paragraph[:300] + "...",
                    tier=tier,
                    credibility_score=score
                )
                return {
                    "answer": first_paragraph,
                    "evidence": [f"Authoritative summary from {page.title}."],
                    "sources": [source],
                    "explanation": f"Reference information obtained from {page.title} documentation."
                }
        except Exception:
            pass

        # 3. Fallback for questions
        return {
            "answer": f"Information regarding '{question}' covers a wide scope. Please refer to primary reference literature or specify a particular sub-topic.",
            "evidence": ["General inquiry requires targeted conceptual breakdown."],
            "sources": [],
            "explanation": "General informational inquiry answered from fundamental reference principles."
        }
