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
        header = abc4ly.convert("regression/header.abc", "")
        self.assertEqual(header['title'], "Hello, world!")

    def test_several_titles(self):
        # The first title is THE title
        header = abc4ly.convert("regression/header_with_several_titles.abc", "")
        self.assertEqual(header['title'], "Hello, world!")

    def test_composer(self):
        header = abc4ly.convert("regression/header.abc", "")
        self.assertEqual(header['composer'], "M. Foo")

    def test_rythm(self):
        header = abc4ly.convert("regression/header.abc", "")
        self.assertEqual(header['rythm'], "reel")

    def test_other(self):
        header = abc4ly.convert("regression/header.abc", "")

class TestMisc(unittest.TestCase):

    def test_no_ending_empty_line(self):
        header = abc4ly.convert("regression/header_no_endl.abc", "")
        self.assertEqual(header['title'], "Hello, world!")

    def test_comments(self):
        abc4ly.convert("regression/header_with_comments.abc", "")

    def test_blank_lines(self):
        # A mix of empty lines, spaces and tabs
        abc4ly.convert("regression/header_with_blank_lines.abc", "")

    def test_only_digits(self):
        self.assertEqual(abc4ly.only_digits("4"), True)
        self.assertEqual(abc4ly.only_digits("457"), True)
        self.assertEqual(abc4ly.only_digits("p"), False)
        self.assertEqual(abc4ly.only_digits("toto"), False)
        self.assertEqual(abc4ly.only_digits("p45t"), False)
        self.assertEqual(abc4ly.only_digits("4pt"), False)
        self.assertEqual(abc4ly.only_digits("p457"), False)
        self.assertEqual(abc4ly.only_digits("42p5"), False)

class TestOutput(unittest.TestCase):

    def test_hello_world(self):
        # A very basic (eventually) syntaxely correct example:
        # title, composer, common time
        abc4ly.convert("regression/hello_world.abc",
                       "regression-out/hello_world.ly")
        self.assert_(filecmp.cmp("regression-out/hello_world.ly",
                                 "regression-ref/hello_world.ly"))

    def test_hello_world_reel(self):
        # Check that the rythm/meter field is written
        # Check the "cut time" meter/time signature
        abc4ly.convert("regression/hello_world_reel.abc",
                       "regression-out/hello_world_reel.ly")
        self.assert_(filecmp.cmp("regression-out/hello_world_reel.ly",
                                 "regression-ref/hello_world_reel.ly"))

    def test_hello_world_empty_rythm(self):
        # Check that a blank rythm does not generate a meter field
        abc4ly.convert("regression/hello_world_empty_rythm.abc",
                       "regression-out/hello_world_empty_rythm.ly")
        self.assert_(filecmp.cmp("regression-out/hello_world_empty_rythm.ly",
                                 "regression-ref/hello_world_empty_rythm.ly"))

    def test_4_4(self):
        # Check that the 4/4 time signature is recognized
        abc4ly.convert("regression/4_4.abc", "regression-out/4_4.ly")
        self.assert_(filecmp.cmp("regression-out/4_4.ly",
                                 "regression-ref/4_4.ly"))

    def test_6_8(self):
        # Check that the 6/8 time signature is recognized
        abc4ly.convert("regression/6_8.abc", "regression-out/6_8.ly")
        self.assert_(filecmp.cmp("regression-out/6_8.ly",
                                 "regression-ref/6_8.ly"))

if __name__ == '__main__':
    unittest.main()
