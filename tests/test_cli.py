import io
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from nolllm.cli import build_parser, main


class CLITests(unittest.TestCase):
    def test_no_question_defaults_to_interactive_mode(self):
        args = build_parser().parse_args([])
        self.assertEqual(args.question, [])
        self.assertFalse(args.tui)

    def test_one_shot_question_is_preserved(self):
        args = build_parser().parse_args(["What", "is", "BM25?"])
        self.assertEqual(args.question, ["What", "is", "BM25?"])
        self.assertFalse(args.tui)

    def test_explicit_tui_flag_is_supported(self):
        args = build_parser().parse_args(["--tui"])
        self.assertTrue(args.tui)
        self.assertEqual(args.question, [])

    def test_one_shot_greeting_skips_research(self):
        output = io.StringIO()
        with patch.object(sys, "argv", ["nollm", "Hi"]), patch(
            "nolllm.cli.answer_question"
        ) as mocked_research, redirect_stdout(output):
            self.assertEqual(main(), 0)

        mocked_research.assert_not_called()
        self.assertIn("Hey!", output.getvalue())


if __name__ == "__main__":
    unittest.main()
