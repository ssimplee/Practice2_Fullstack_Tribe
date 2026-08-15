"""Automated tests for Person 3's Translation & Summary skills.

Discovered by Run Tests.cmd, which runs from CampusBot/:
    python -m unittest discover -s tests -p "test_*.py" -v

Deterministic: these tests do NOT require Ollama or the local model.
They cover the lab's recommended case #3 (translation routing) plus
summary routing, success/failure behaviour, and Chinese input.
"""

import unittest

from app.llm import LLMBackend, StaticBackend
from app.skills.registration_example import build_runtime


class _FailingBackend:
    """LLM backend stub that always raises, for error-path testing."""

    def ask(self, prompt: str) -> str:
        raise RuntimeError("intentional failure for testing")


class TranslationSkillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = build_runtime(
            llm=StaticBackend("mock-translation")
        )

    def test_translate_routes_to_translation(self):
        r = self.runtime.execute(
            "user01", 'Translate "Welcome" into Chinese.'
        )
        self.assertEqual(r["skill"], "translation")
        self.assertEqual(r["status"], "success")

    def test_translate_success_returns_llm_response(self):
        r = self.runtime.execute(
            "user01", 'Translate "hello" into Chinese.'
        )
        self.assertEqual(r["skill"], "translation")
        self.assertEqual(r["status"], "success")
        self.assertEqual(r["response"], "mock-translation")

    def test_translate_no_target_language(self):
        r = self.runtime.execute(
            "user01", 'Translate "hello"'
        )
        self.assertEqual(r["skill"], "translation")
        self.assertIn("target language", r["response"].lower())

    def test_translate_no_source_text(self):
        r = self.runtime.execute(
            "user01", "Translate into Chinese."
        )
        self.assertEqual(r["skill"], "translation")
        self.assertIn("provide", r["response"].lower())

    def test_translate_chinese_to_english(self):
        r = self.runtime.execute(
            "user01", '把"深圳大学"翻译成英文'
        )
        self.assertEqual(r["skill"], "translation")
        self.assertEqual(r["status"], "success")

    def test_translate_not_matched_by_summary(self):
        """Summary requests must not be stolen by TranslationSkill."""
        r = self.runtime.execute(
            "user01", "Summarize: some long text here"
        )
        self.assertNotEqual(r["skill"], "translation")

    def test_translate_llm_failure_returns_error(self):
        runtime = build_runtime(llm=_FailingBackend())
        r = runtime.execute(
            "user01", 'Translate "hello" into Chinese.'
        )
        self.assertEqual(r["skill"], "translation")
        self.assertEqual(r["status"], "error")


class SummarySkillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = build_runtime(
            llm=StaticBackend("mock-summary")
        )

    def test_summary_routes_to_summary(self):
        r = self.runtime.execute(
            "user01", "Summarize: Shenzhen University was founded in 1983."
        )
        self.assertEqual(r["skill"], "summary")
        self.assertEqual(r["status"], "success")

    def test_summary_success_returns_llm_response(self):
        r = self.runtime.execute(
            "user01", "Summarize: some text to summarise here"
        )
        self.assertEqual(r["skill"], "summary")
        self.assertEqual(r["status"], "success")
        self.assertEqual(r["response"], "mock-summary")

    def test_summary_no_text_placeholder(self):
        r = self.runtime.execute("user01", "Summarize this.")
        self.assertEqual(r["skill"], "summary")
        self.assertIn("provide", r["response"].lower())

    def test_summary_no_text_empty(self):
        r = self.runtime.execute("user01", "Summarize:")
        self.assertEqual(r["skill"], "summary")
        self.assertIn("provide", r["response"].lower())

    def test_summary_chinese_request(self):
        r = self.runtime.execute(
            "user01", "总结：深圳大学成立于1983年，有两个校区。"
        )
        self.assertEqual(r["skill"], "summary")
        self.assertEqual(r["status"], "success")

    def test_summary_llm_failure_returns_error(self):
        runtime = build_runtime(llm=_FailingBackend())
        r = runtime.execute(
            "user01", "Summarize: some text here"
        )
        self.assertEqual(r["skill"], "summary")
        self.assertEqual(r["status"], "error")


class RoutingEdgeCaseTests(unittest.TestCase):
    """Verify Translation/Summary do not steal Campus/Library requests."""

    @classmethod
    def setUpClass(cls):
        cls.runtime = build_runtime(
            llm=StaticBackend("mock-response")
        )

    def test_campus_not_stolen_by_translation(self):
        r = self.runtime.execute(
            "user01", "What is Shenzhen University's motto?"
        )
        self.assertEqual(r["skill"], "campus")

    def test_library_not_stolen_by_summary(self):
        r = self.runtime.execute(
            "user01", "Where is the library?"
        )
        self.assertEqual(r["skill"], "library")


def _composition_llm(prompt: str) -> str:
    """Deterministic LLM stub for composition tests.

    Returns different responses based on which step of the chain
    is calling: summary step or translation step.
    """
    lower = prompt.lower()
    if "summarise" in lower or "summarize" in lower:
        return "Shenzhen University was founded in 1983."
    if "translate" in lower:
        return "深圳大学成立于1983年。"
    return "mock"


class CompositionSkillTests(unittest.TestCase):
    """Tests for the Campus → Summary → Translation composition chain."""

    @classmethod
    def setUpClass(cls):
        cls.runtime = build_runtime(
            llm=StaticBackend(_composition_llm)
        )

    def test_composition_routes_to_composition(self):
        r = self.runtime.execute(
            "user01",
            "Tell me briefly when Shenzhen University was founded "
            "and answer in Chinese.",
        )
        self.assertEqual(r["skill"], "composition")
        self.assertEqual(r["status"], "success")

    def test_composition_success_returns_translation(self):
        r = self.runtime.execute(
            "user01",
            "Tell me briefly when Shenzhen University was founded "
            "and answer in Chinese.",
        )
        self.assertEqual(r["skill"], "composition")
        # The final output is the translation step's response.
        self.assertEqual(r["response"], "深圳大学成立于1983年。")

    def test_composition_does_not_steal_campus_only(self):
        r = self.runtime.execute(
            "user01", "When was Shenzhen University founded?"
        )
        self.assertEqual(r["skill"], "campus")

    def test_composition_does_not_steal_translation_only(self):
        r = self.runtime.execute(
            "user01", 'Translate "hello" into Chinese.'
        )
        self.assertEqual(r["skill"], "translation")

    def test_composition_does_not_steal_summary_only(self):
        r = self.runtime.execute(
            "user01", "Summarize: some text here"
        )
        self.assertEqual(r["skill"], "summary")

    def test_composition_llm_failure_returns_error(self):
        runtime = build_runtime(llm=_FailingBackend())
        r = runtime.execute(
            "user01",
            "Tell me briefly when Shenzhen University was founded "
            "and answer in Chinese.",
        )
        self.assertEqual(r["skill"], "composition")
        self.assertEqual(r["status"], "error")


if __name__ == "__main__":
    unittest.main()
