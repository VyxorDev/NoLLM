import unittest

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
        async with app.run_test() as pilot:
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


if __name__ == "__main__":
    unittest.main()
