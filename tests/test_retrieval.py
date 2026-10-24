import unittest

from nolllm.models import Document
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


if __name__ == "__main__":
    unittest.main()
