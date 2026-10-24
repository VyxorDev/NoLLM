import unittest

from nolllm.compose import compose
from nolllm.models import Document, Evidence
from nolllm.retrieval import retrieve


class RetrievalTests(unittest.TestCase):
    def test_relevant_sentence_ranks_first(self):
        docs = [
            Document(
                title="GPU notes",
                url="https://example.test/gpu",
                text=(
                    "Bananas are a common fruit grown in tropical climates. "
                    "The RTX 5060 benchmark reached 92 frames per second while the RTX 4060 reached 71 frames per second. "
                    "The test used the same graphics settings for both cards."
                ),
            )
        ]
        evidence = retrieve("Is RTX 5060 faster than RTX 4060?", docs, limit=3)
        self.assertTrue(evidence)
        self.assertIn("92 frames per second", evidence[0].sentence)

    def test_two_concept_query_rejects_partial_match(self):
        docs = [
            Document(
                title="Personal knowledge base",
                url="https://example.test/personal-kb",
                text="A personal knowledge base stores distilled facts and notes for an individual user.",
            ),
            Document(
                title="Knowledge graph",
                url="https://example.org/knowledge-graph",
                text="A knowledge graph represents entities and relationships as connected nodes and edges.",
            ),
        ]
        evidence = retrieve("What is a knowledge graph?", docs, limit=8)
        self.assertEqual(len(evidence), 1)
        self.assertIn("knowledge graph", evidence[0].sentence.lower())
        self.assertEqual(evidence[0].query_coverage, 1.0)

    def test_unrelated_query_returns_no_evidence(self):
        docs = [
            Document(
                title="Fruit notes",
                url="https://example.test/fruit",
                text="Bananas are common fruit grown in tropical climates around the world.",
            )
        ]
        self.assertEqual(retrieve("What is a knowledge graph?", docs), [])

    def test_composer_prefers_distinct_publishers(self):
        evidence = [
            Evidence(
                sentence="Python is a programming language used for many kinds of software development.",
                title="Python overview",
                url="https://news.example.com/python",
                score=4.0,
                matched_terms=("python",),
                query_coverage=1.0,
            ),
            Evidence(
                sentence="Python supports modules that help developers organize larger applications.",
                title="Python modules",
                url="https://news.example.com/modules",
                score=3.0,
                matched_terms=("python",),
                query_coverage=1.0,
            ),
            Evidence(
                sentence="Python is widely used for scripting and automation tasks.",
                title="Python guide",
                url="https://other.example.org/python",
                score=2.0,
                matched_terms=("python",),
                query_coverage=1.0,
            ),
        ]
        answer = compose("What is Python?", evidence, max_points=2)
        self.assertEqual(len(answer.evidence), 2)
        self.assertEqual(
            [item.url for item in answer.evidence],
            ["https://news.example.com/python", "https://other.example.org/python"],
        )


if __name__ == "__main__":
    unittest.main()
