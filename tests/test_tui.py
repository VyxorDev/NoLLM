import unittest
from unittest.mock import patch

try:
    import textual  # noqa: F401
except ModuleNotFoundError:
    textual = None


@unittest.skipIf(textual is None, "install the optional .[tui] extra to run TUI tests")
class TUITests(unittest.IsolatedAsyncioTestCase):
    async def test_tui_mounts_chat_controls(self):
        from textual.widgets import Input, RichLog

        from nolllm.tui import NoLLMApp

        app = NoLLMApp(web_enabled=False)
        async with app.run_test():
            self.assertIsNotNone(app.query_one("#prompt", Input))
            self.assertIsNotNone(app.query_one("#transcript", RichLog))
            self.assertFalse(app.web_enabled)

    async def test_offline_command_disables_web_research(self):
        from nolllm.tui import NoLLMApp

        app = NoLLMApp(web_enabled=True)
        async with app.run_test() as pilot:
            await pilot.click("#prompt")
            await pilot.press(*list("/offline"), "enter")
            self.assertFalse(app.web_enabled)

    async def test_wiki_limit_and_direct_urls_are_preserved(self):
        from nolllm.models import Answer
        from nolllm.tui import NoLLMApp

        answer = Answer(question="sample", text="sample answer", evidence=[], confidence=0.5)
        with patch("nolllm.tui.answer_question", return_value=answer) as mocked:
            app = NoLLMApp(
                initial_urls=["https://example.test/page"],
                wiki_enabled=False,
                wiki_limit=2,
            )
            async with app.run_test() as pilot:
                await pilot.click("#prompt")
                await pilot.press(*list("sample question"), "enter")
                await pilot.pause(0.2)
                mocked.assert_called_once()
                self.assertEqual(mocked.call_args.kwargs["urls"], ["https://example.test/page"])
                self.assertEqual(mocked.call_args.kwargs["wiki_limit"], 2)
                self.assertFalse(mocked.call_args.kwargs["use_wikipedia"])
                self.assertFalse(app._busy)

    async def test_greeting_does_not_start_research(self):
        from nolllm.tui import NoLLMApp

        app = NoLLMApp(web_enabled=False)
        with patch("nolllm.tui.answer_question") as mocked_research, patch.object(
            NoLLMApp, "_log", autospec=True
        ) as mocked_log:
            async with app.run_test() as pilot:
                await pilot.click("#prompt")
                await pilot.press("h", "i", "enter")
                await pilot.pause(0.1)

            mocked_research.assert_not_called()
            self.assertTrue(
                any(
                    call.args[1] == "NOLLM" and "Hey!" in call.args[2]
                    for call in mocked_log.call_args_list
                )
            )

    async def test_question_about_hi_still_starts_research(self):
        from nolllm.models import Answer
        from nolllm.tui import NoLLMApp

        answer = Answer(question="What does hi mean?", text="A sample answer.", evidence=[], confidence=0.2)
        with patch("nolllm.tui.answer_question", return_value=answer) as mocked_research:
            app = NoLLMApp(web_enabled=False)
            async with app.run_test() as pilot:
                await pilot.click("#prompt")
                await pilot.press(*list("what does the word hi mean?"), "enter")
                await pilot.pause(0.2)
                mocked_research.assert_called_once()


if __name__ == "__main__":
    unittest.main()
