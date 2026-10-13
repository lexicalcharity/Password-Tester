"""Tests for password_checker. Run from the project folder with: python -m unittest"""

import hashlib
import io
import unittest
from unittest import mock

import password_checker as checker


class RequirementTests(unittest.TestCase):
    def failed(self, password):
        requirements, _ = checker.check_requirements(password)
        return [description for description, passed in requirements if not passed]

    def test_all_requirements_met(self):
        self.assertEqual(self.failed("x7#Lq9!vR2mZ"), [])

    def test_too_short(self):
        self.assertEqual(self.failed("x7#Lq9!v"), ["At least 12 characters long"])

    def test_each_character_type_missing(self):
        self.assertIn("At least 1 uppercase letter (A-Z)", self.failed("x7#lq9!vr2mz"))
        self.assertIn("At least 1 lowercase letter (a-z)", self.failed("X7#LQ9!VR2MZ"))
        self.assertIn("At least 1 digit (0-9)", self.failed("xq#Lqb!vRwmZ"))
        self.assertIn("At least 1 special character (!, @, #, etc.)", self.failed("x7kLq9mvR2mZ"))

    def test_spaces_are_kept(self):
        # Leading/trailing spaces count towards the length and as special characters
        self.assertEqual(self.failed("  Gold7Mz7Pq  "), [])

    def test_long_passphrase_skips_character_rules(self):
        requirements, is_passphrase = checker.check_requirements("correct horse battery staple")
        self.assertTrue(is_passphrase)
        self.assertTrue(all(passed for _, passed in requirements))


class CommonPasswordTests(unittest.TestCase):
    def test_common_passwords_detected(self):
        for password in ["Password@123!", "P@ssw0rd2024!", "Welcome2024!", "Pa$$word123", "!!Dragon99"]:
            with self.subTest(password=password):
                self.assertTrue(checker.is_common_password(password))

    def test_uncommon_password_not_flagged(self):
        self.assertFalse(checker.is_common_password("Kept!Ztrong91#Q"))


class PatternTests(unittest.TestCase):
    def warnings(self, password):
        return checker.estimate_strength(password)[1]

    def test_sequences(self):
        self.assertIn("Contains an ascending letter sequence ('xyz')", self.warnings("Tr0ub4dor&3xyz"))
        self.assertIn("Contains a descending letter sequence ('xwvu')", self.warnings("Gold#Mxwvu9Pq!"))
        self.assertIn("Contains an ascending digit sequence ('2345')", self.warnings("Qwerty!2345Ab"))
        self.assertIn("Contains a descending digit sequence ('9876')", self.warnings("Asdf#9876Lkjh"))

    def test_keyboard_patterns(self):
        self.assertIn("Contains a keyboard pattern ('Lkjh')", self.warnings("Asdf#9876Lkjh"))
        self.assertIn("Contains a keyboard pattern ('1qaz')", self.warnings("1qaz#Mz7Pq!kR"))

    def test_repeated_characters(self):
        self.assertIn("Contains repeated characters ('aaa')", self.warnings("Gold#Mzaaa7Pq!"))

    def test_leetspeak_word(self):
        self.assertIn("Contains a common word ('dr4g0n')", self.warnings("Xy#dr4g0n!Mz7Pq"))

    def test_random_password_has_no_warnings(self):
        self.assertEqual(self.warnings("Kept!Ztrong91#Q"), [])


class EvaluateTests(unittest.TestCase):
    def test_empty(self):
        evaluation = checker.evaluate("")
        self.assertEqual(evaluation.rating, "")
        self.assertEqual(evaluation.level, 0)

    def test_ratings(self):
        cases = {
            "Short1!": "Weak",                     # Fails a requirement
            "Password@123!": "Weak",               # Common password
            "Qwerty!2345Ab": "Weak",               # Mostly patterns
            "Gold#Mxwvu9Pq!": "Good",
            "x7#Lq9!vR2mZ": "Strong",
            "correct horse battery staple": "Strong",
        }
        for password, rating in cases.items():
            with self.subTest(password=password):
                self.assertEqual(checker.evaluate(password).rating, rating)

    def test_patterns_lower_the_score(self):
        self.assertLess(checker.evaluate("Abcdef#123456").bits, checker.evaluate("Kept!Ztrong91").bits)


class BreachTests(unittest.TestCase):
    def fake_response(self, password, count):
        # Simulate the API: return a line for this password's hash suffix plus an unrelated line
        suffix = hashlib.sha1(password.encode()).hexdigest().upper()[5:]
        body = f"0000000000000000000000000000000000A:5\r\n{suffix}:{count}\r\n"
        return io.BytesIO(body.encode())

    def test_breached_password(self):
        with mock.patch("urllib.request.urlopen", return_value=self.fake_response("password", 123)) as urlopen:
            self.assertEqual(checker.check_breach("password"), 123)
        # Only the 5-character hash prefix is sent, never the password
        url = urlopen.call_args[0][0].full_url
        self.assertEqual(url, "https://api.pwnedpasswords.com/range/5BAA6")

    def test_safe_password(self):
        with mock.patch("urllib.request.urlopen", return_value=self.fake_response("something else", 7)):
            self.assertEqual(checker.check_breach("password"), 0)

    def test_network_error_is_raised(self):
        with mock.patch("urllib.request.urlopen", side_effect=OSError("offline")):
            with self.assertRaises(OSError):
                checker.check_breach("password")


if __name__ == "__main__":
    unittest.main()
