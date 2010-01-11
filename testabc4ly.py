#!/usr/bin/env python
# -*- coding:utf-8 -*-

import abc4ly
import unittest
import filecmp

# unittest reminder:
# assert functions: assertEqual(), assertRaises() and assert_(condition)

class TestFileOperations(unittest.TestCase):

    def test_open_failure(self):
        self.assertRaises(IOError, abc4ly.open_abc,
                          "regression/missing.abc")

    def test_open_success(self):
        tmp = abc4ly.open_abc("regression/empty.abc")
        tmp.close()

class TestInformationFields(unittest.TestCase):

    def test_title(self):
        header = abc4ly.create_empty_header()
        abc4ly.read_line("T:Hello, world!\n", header)
        self.assertEqual(header['title'], "Hello, world!")

    def test_several_titles(self):
        # The first title is THE title
        header = abc4ly.create_empty_header()
        abc4ly.read_line("T:Hello, world!\n", header)
        abc4ly.read_line("C:M. Foo!\n", header)
        abc4ly.read_line("T:Welcome to the cruel world\n", header)
        self.assertEqual(header['title'], "Hello, world!")

    def test_composer(self):
        header = abc4ly.create_empty_header()
        abc4ly.read_line("C:M. Foo\n", header)
        self.assertEqual(header['composer'], "M. Foo")

    def test_rythm(self):
        header = abc4ly.create_empty_header()
        abc4ly.read_line("R:reel\n", header)
        self.assertEqual(header['rythm'], "reel")

    def test_other(self):
        header = abc4ly.create_empty_header()
        abc4ly.read_line("I:No comment\n", header)

class TestMisc(unittest.TestCase):

    def test_no_ending_empty_line(self):
        header = abc4ly.create_empty_header()
        with open("regression/header_no_endl.abc") as tmp:
            for line in tmp.readlines():
                abc4ly.read_line(line, header)
        self.assertEqual(header['title'], "Hello, world!")

    def test_comments(self):
        # Check that comments are handled silently
        header = abc4ly.create_empty_header()
        with open("regression/header_with_comments.abc") as tmp:
            for line in tmp.readlines():
                abc4ly.read_line(line, header)

    def test_blank_lines(self):
        # A mix of empty lines, spaces and tabs
        header = abc4ly.create_empty_header()
        with open("regression/header_with_blank_lines.abc") as tmp:
            for line in tmp.readlines():
                abc4ly.read_line(line, header)

    def test_only_digits(self):
        self.assertEqual(abc4ly.only_digits("4"), True)
        self.assertEqual(abc4ly.only_digits("457"), True)
        self.assertEqual(abc4ly.only_digits("p"), False)
        self.assertEqual(abc4ly.only_digits("toto"), False)
        self.assertEqual(abc4ly.only_digits("p45t"), False)
        self.assertEqual(abc4ly.only_digits("4pt"), False)
        self.assertEqual(abc4ly.only_digits("p457"), False)
        self.assertEqual(abc4ly.only_digits("42p5"), False)

class TestTimeSignature(unittest.TestCase):
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

    def test_with_spaces(self):
        # Check that a time signature including spaces is recognized
        abc4ly.convert("regression/4_4_with_spaces.abc",
                       "regression-out/4_4.ly")
        self.assert_(filecmp.cmp("regression-out/4_4.ly",
                                 "regression-ref/4_4.ly"))

    def test_invalid(self):
        # Check that a syntactically incorrect time signature raises an
        # exception
        self.assertRaises(abc4ly.AbcSyntaxError, abc4ly.convert,
                          "regression/invalid_time_signature.abc", "")

    def test_missing(self):
        # Check that a mising time signature raises an exception
        self.assertRaises(abc4ly.AbcSyntaxError, abc4ly.convert,
                          "regression/missing_time_signature.abc", "")

class TestKeySignature(unittest.TestCase):

    def test_major_keys(self):
        self.assertEqual(abc4ly.translate_key_signature("K:C"), "\key c \major")

    def test_invalid_key(self):
        self.assertRaises(abc4ly.AbcSyntaxError, abc4ly.translate_key_signature, "K:s")
        self.assertRaises(abc4ly.AbcSyntaxError, abc4ly.translate_key_signature, "K:")
        self.assertRaises(abc4ly.AbcSyntaxError, abc4ly.translate_key_signature, "K:ceolien")
        self.assertRaises(abc4ly.AbcSyntaxError, abc4ly.translate_key_signature, "K:cio")

    def test_accidentals(self):
        self.assertEqual(abc4ly.translate_key_signature("K:Bb"), "\key bes \major")
        self.assertEqual(abc4ly.translate_key_signature("K:F#"), "\key fis \major")

    def test_modes(self):
        self.assertEqual(abc4ly.translate_key_signature("K:Am"), "\key a \minor")
        self.assertEqual(abc4ly.translate_key_signature("K:G minor"),
                         "\key g \minor")
        self.assertEqual(abc4ly.translate_key_signature("K:Eb minor"),
                         "\key ees \minor")
        self.assertEqual(abc4ly.translate_key_signature("K:D mixolydian"),
                         "\key d \mixolydian")
        self.assertEqual(abc4ly.translate_key_signature("K:DMix"),
                         "\key d \mixolydian")
        self.assertEqual(abc4ly.translate_key_signature("K:Dmix"),
                         "\key d \mixolydian")
        for mode in [ "ionian", "dorian", "phrygian", "lydian", "mixolydian",
                          "aeolian", "minor", "locrian" ]:
            abc_signature = "K:D {0}".format(mode)
            ly_signature = "\key d \{0}".format(mode)
            self.assertEqual(abc4ly.translate_key_signature(abc_signature),
                             ly_signature)


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

    def test_c_major(self):
        # The C major scale
        abc4ly.convert("regression/c_major.abc",
                       "regression-out/c_major.ly")
        self.assert_(filecmp.cmp("regression-out/c_major.ly",
                                 "regression-ref/c_major.ly"))

if __name__ == '__main__':
    unittest.main()
