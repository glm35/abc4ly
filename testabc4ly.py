#!/usr/bin/env python
# -*- coding:utf-8 -*-

import abc4ly
import unittest

# unittest reminder:
# assert functions: assertEqual(), assertRaises() and assert_(condition)

class TestFileOperations(unittest.TestCase):

    def test_open_failure(self):
        self.assertRaises(IOError, abc4ly.convert,
                          "regression/missing.abc", "")

    def test_open_success(self):
        abc4ly.convert("regression/empty.abc", "")

class TestInformationFields(unittest.TestCase):

    def test_title(self):
        abc4ly.convert("regression/header.abc", "")
        self.assertEqual(abc4ly.title, "Hello, world!")

    def test_composer(self):
        abc4ly.convert("regression/header.abc", "")
        self.assertEqual(abc4ly.composer, "M. Foo")

    def test_rythm(self):
        abc4ly.convert("regression/header.abc", "")
        self.assertEqual(abc4ly.rythm, "reel")

    def test_other(self):
        abc4ly.convert("regression/header.abc", "")

class TestMisc(unittest.TestCase):

    def test_no_ending_empty_line(self):
        abc4ly.convert("regression/header_no_endl.abc", "")
        self.assertEqual(abc4ly.title, "Hello, world!")

    def test_comments(self):
        abc4ly.convert("regression/header_with_comments.abc", "")

    def test_blank_lines(self):
        # A mix of empty lines, spaces and tabs
        abc4ly.convert("regression/header_with_blank_lines.abc", "")

if __name__ == '__main__':
    unittest.main()
