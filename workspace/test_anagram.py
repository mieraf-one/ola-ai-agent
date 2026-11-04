import unittest
from anagram import is_anagram

class TestAnagramChecker(unittest.TestCase):
    def test_basic_anagrams(self):
        self.assertTrue(is_anagram("listen", "silent"))
        self.assertTrue(is_anagram("triangle", "integral"))
        self.assertFalse(is_anagram("apple", "papelz"))

    def test_case_insensitivity(self):
        self.assertTrue(is_anagram("Listen", "Silent"))
        self.assertTrue(is_anagram("Debit Card", "Bad Credit"))

    def test_whitespace_handling(self):
        self.assertTrue(is_anagram("the eyes", "they see"))
        self.assertTrue(is_anagram("hello", "o l l e h "))

    def test_non_anagrams(self):
        self.assertFalse(is_anagram("hello", "world"))
        self.assertFalse(is_anagram("test", "t"))

if __name__ == '__main__':
    unittest.main()
