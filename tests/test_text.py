import unittest

from nolllm.text import html_to_text, tokenize


class TextTests(unittest.TestCase):
    def test_html_ignores_script(self):
        text = html_to_text("<html><body>Hello world.<script>evil()</script><p>Useful fact.</p></body></html>")
        self.assertIn("Hello world", text)
        self.assertIn("Useful fact", text)
        self.assertNotIn("evil", text)

    def test_tokenize_removes_common_stopwords(self):
        self.assertEqual(tokenize("What is the Python API?"), ["python", "api"])


if __name__ == "__main__":
    unittest.main()
