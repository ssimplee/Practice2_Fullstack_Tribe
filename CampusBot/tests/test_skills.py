"""Automated tests for Person 2's Campus & Library skills.

Discovered by Run Tests.cmd, which runs from CampusBot/:
    python -m unittest discover -s tests -p "test_*.py" -v

Deterministic: these tests do NOT require Ollama or the local model.
They cover the lab's recommended cases #1 (campus), #2 (library) and
#6 (missing knowledge does not produce an invented answer), plus
routing edge cases and Chinese input.
"""

import unittest

from app.skills.registration_example import build_runtime


class CampusLibrarySkillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = build_runtime()

    # --- Campus: known facts ---
    def test_campus_motto(self):
        r = self.runtime.execute("user01", "What is Shenzhen University's motto?")
        self.assertEqual(r["skill"], "campus")
        self.assertEqual(r["status"], "success")
        self.assertIn("self-reliance", r["response"].lower())

    def test_campus_founded(self):
        r = self.runtime.execute("user01", "When was Shenzhen University founded?")
        self.assertEqual(r["skill"], "campus")
        self.assertIn("1983", r["response"])

    def test_campus_two_campuses(self):
        r = self.runtime.execute("user01", "What are Shenzhen University's two campuses?")
        self.assertEqual(r["skill"], "campus")
        self.assertIn("Yuehai", r["response"])
        self.assertIn("Lihu", r["response"])

    def test_campus_abbreviation(self):
        r = self.runtime.execute("user01", "What is SZU's abbreviation?")
        self.assertEqual(r["skill"], "campus")
        self.assertIn("SZU", r["response"])

    # --- Library: known facts ---
    def test_library_location(self):
        r = self.runtime.execute("user01", "Where is Shenzhen University Library?")
        self.assertEqual(r["skill"], "library")
        self.assertIn("Nanhai Avenue", r["response"])

    def test_library_info(self):
        r = self.runtime.execute("user01", "What library information is available?")
        self.assertEqual(r["skill"], "library")
        self.assertIn("North Library", r["response"])

    # --- Missing information: must NOT fabricate ---
    def test_president_no_fabrication(self):
        r = self.runtime.execute("user01", "Who is the current president of Shenzhen University?")
        self.assertEqual(r["skill"], "campus")
        self.assertIn("don't have enough", r["response"].lower())
        self.assertNotIn("Nanhai Avenue", r["response"])

    def test_international_office_no_fabrication(self):
        r = self.runtime.execute("user01", "Where is Shenzhen University's International Office?")
        self.assertEqual(r["skill"], "campus")
        self.assertIn("don't have enough", r["response"].lower())
        self.assertNotIn("Nanhai Avenue", r["response"])

    def test_ranking_no_fabrication(self):
        r = self.runtime.execute("user01", "What is Shenzhen University's QS ranking?")
        self.assertEqual(r["skill"], "campus")
        self.assertIn("don't have enough", r["response"].lower())

    # --- Routing edge cases ---
    def test_library_not_stolen_by_campus(self):
        r = self.runtime.execute("user01", "Where is the university library?")
        self.assertEqual(r["skill"], "library")

    def test_translate_deferred_to_unmatched(self):
        r = self.runtime.execute("user01", "Translate welcome into Chinese.")
        self.assertIsNone(r["skill"])
        self.assertEqual(r["status"], "unmatched")

    def test_out_of_scope_unmatched(self):
        r = self.runtime.execute("user01", "Where is the International Office?")
        self.assertIsNone(r["skill"])
        self.assertEqual(r["status"], "unmatched")

    # --- Runtime-level ---
    def test_empty_message_invalid(self):
        r = self.runtime.execute("user01", "   ")
        self.assertIsNone(r["skill"])
        self.assertEqual(r["status"], "invalid_request")

    # --- Chinese ---
    def test_chinese_founded(self):
        r = self.runtime.execute("user01", "深圳大学是哪一年成立的？")
        self.assertEqual(r["skill"], "campus")
        self.assertIn("1983", r["response"])


if __name__ == "__main__":
    unittest.main()
