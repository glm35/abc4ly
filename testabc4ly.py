#!/usr/bin/env python
# -*- coding:utf-8 -*-

import abc4ly
import unittest
import filecmp

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

    def test_several_titles(self):
        # The first title is THE title
        abc4ly.convert("regression/header_with_several_titles.abc", "")
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

class TestOutput(unittest.TestCase):

    def test_hello_world(self):
        # A very simple, very basic example
        abc4ly.convert("regression/hello_world.abc",
                       "regression-out/hello_world.ly")
        self.assert_(filecmp.cmp("regression-out/hello_world.ly",
                                 "regression-ref/hello_world.ly"))

if __name__ == '__main__':
    unittest.main()
