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

if __name__ == '__main__':
    unittest.main()
