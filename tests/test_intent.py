import unittest

from nolllm.intent import respond_to_conversation


class IntentTests(unittest.TestCase):
    def test_common_greetings_get_a_conversational_reply(self):
        for message in ("Hi", "hello!", "HEY THERE", "good morning", "hi 👋"):
            with self.subTest(message=message):
                reply = respond_to_conversation(message)
                self.assertIsNotNone(reply)
                self.assertIn("NoLLM", reply)

    def test_thanks_and_goodbyes_are_recognized(self):
        self.assertIn("welcome", respond_to_conversation("thanks").lower())
        self.assertIn("See you", respond_to_conversation("bye"))

    def test_identity_and_capability_questions_get_direct_answers(self):
        self.assertIn("research engine", respond_to_conversation("who are you").lower())
        self.assertIn("local file", respond_to_conversation("what can you do").lower())

    def test_real_questions_about_the_word_hi_still_go_to_research(self):
        self.assertIsNone(respond_to_conversation("What does the word hi mean?"))
        self.assertIsNone(respond_to_conversation("Hi, can you explain Python?"))

    def test_unknown_input_is_not_misclassified_as_small_talk(self):
        self.assertIsNone(respond_to_conversation("Explain how a knowledge graph works."))


if __name__ == "__main__":
    unittest.main()
