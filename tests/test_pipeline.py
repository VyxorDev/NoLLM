import tempfile
import unittest
from pathlib import Path

from nolllm.pipeline import answer_question


class PipelineTests(unittest.TestCase):
    def test_offline_file_pipeline(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "notes.txt"
            path.write_text(
                "BM25 is a ranking function used by information retrieval systems. "
                "It scores documents using term frequency and inverse document frequency.",
                encoding="utf-8",
            )
            answer = answer_question(
                "What is BM25 used for?",
                files=[str(path)],
                use_wikipedia=False,
            )
            self.assertGreater(answer.confidence, 0)
            self.assertIn("ranking function", answer.text)


if __name__ == "__main__":
    unittest.main()
