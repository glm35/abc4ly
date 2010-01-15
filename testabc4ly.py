#!/usr/bin/env python
# -*- coding:utf-8 -*-

import unittest
import filecmp

import abc4ly
from abc4ly import *

# unittest reminder:
# assert functions: assertEqual(), assertRaises() and assert_(condition)

class TestFileOperations(unittest.TestCase):

    def test_open_failure(self):
        self.assertRaises(IOError, open_abc,
                          "regression/missing.abc")

    def test_open_success(self):
        tmp = open_abc("regression/empty.abc")
        tmp.close()

class TestInformationFields(unittest.TestCase):

    def test_title(self):
        tc = TuneContext()
        read_line(tc, "T:Hello, world!\n")
        self.assertEqual(tc.title, "Hello, world!")

    def test_several_titles(self):
        # The first title is THE title
        tc = TuneContext()
        read_line(tc, "T:Hello, world!\n")
        read_line(tc, "C:M. Foo!\n")
        read_line(tc, "T:Welcome to the cruel world\n")
        self.assertEqual(tc.title, "Hello, world!")

    def test_composer(self):
        tc = TuneContext()
        read_line(tc, "C:M. Foo\n")
        self.assertEqual(tc.composer, "M. Foo")

    def test_rythm(self):
        tc = TuneContext()
        read_line(tc, "R:reel\n")
        self.assertEqual(tc.rythm, "reel")

    def test_other(self):
        tc = TuneContext()
        read_line(tc, "I:No comment\n")

class TestMisc(unittest.TestCase):

    def test_no_ending_empty_line(self):
        tc = TuneContext()
        with open("regression/header_no_endl.abc") as tmp:
            for line in tmp.readlines():
                read_line(tc, line)
        self.assertEqual(tc.title, "Hello, world!")

    def test_comments(self):
        # Check that comments are handled silently
        tc = TuneContext()
        with open("regression/header_with_comments.abc") as tmp:
            for line in tmp.readlines():
                read_line(tc, line)

    def test_blank_lines(self):
        # A mix of empty lines, spaces and tabs
        tc = TuneContext()
        with open("regression/header_with_blank_lines.abc") as tmp:
            for line in tmp.readlines():
                read_line(tc, line)

    def test_get_leading_digits(self):
        self.assertEqual(get_leading_digits("123"), "123")
        self.assertEqual(get_leading_digits("8"), "8")
        self.assertEqual(get_leading_digits("54abc"), "54")
        self.assertEqual(get_leading_digits("ab123"), "")
        self.assertEqual(get_leading_digits(""), "")
        self.assertEqual(get_leading_digits("   123"), "")


class TestTimeSignature(unittest.TestCase):

    def test_normalize_time_signature(self):
        self.assertEqual(normalize_time_signature("C"), "4/4")
        self.assertEqual(normalize_time_signature("C|"), "2/2")
        self.assertEqual(normalize_time_signature("4/4"), "4/4")
        self.assertEqual(normalize_time_signature("12/8"), "12/8")

        # Check that a time signature including spaces is recognized
        self.assertEqual(normalize_time_signature(" 4 /   4"), "4/4")
        
        # Check that a syntactically incorrect time signature raises an
        # exception
        self.assertRaises(AbcSyntaxError, normalize_time_signature, "4/foo")

    def test_missing(self):
        # Check that a mising time signature raises an exception
        self.assertRaises(AbcSyntaxError, convert,
                          "regression/missing_time_signature.abc", "")


class TestKeySignature(unittest.TestCase):

    def test_major_keys(self):
        self.assertEqual(translate_key_signature("K:C"), "\key c \major")

    def test_invalid_key(self):
        self.assertRaises(AbcSyntaxError, translate_key_signature, "K:s")
        self.assertRaises(AbcSyntaxError, translate_key_signature, "K:")
        self.assertRaises(AbcSyntaxError, translate_key_signature, "K:ceolien")
        self.assertRaises(AbcSyntaxError, translate_key_signature, "K:cio")

    def test_accidentals(self):
        self.assertEqual(translate_key_signature("K:Bb"), "\key bes \major")
        self.assertEqual(translate_key_signature("K:F#"), "\key fis \major")

    def test_modes(self):
        self.assertEqual(translate_key_signature("K:Am"), "\key a \minor")
        self.assertEqual(translate_key_signature("K:G minor"),
                         "\key g \minor")
        self.assertEqual(translate_key_signature("K:Eb minor"),
                         "\key ees \minor")
        self.assertEqual(translate_key_signature("K:D mixolydian"),
                         "\key d \mixolydian")
        self.assertEqual(translate_key_signature("K:DMix"),
                         "\key d \mixolydian")
        self.assertEqual(translate_key_signature("K:Dmix"),
                         "\key d \mixolydian")
        for mode in [ "ionian", "dorian", "phrygian", "lydian", "mixolydian",
                          "aeolian", "minor", "locrian" ]:
            abc_signature = "K:D {0}".format(mode)
            ly_signature = "\key d \{0}".format(mode)
            self.assertEqual(translate_key_signature(abc_signature),
                             ly_signature)


class TestNoteDuration(unittest.TestCase):

    def test_get_default_note_duration(self):
        self.assertEqual(get_default_note_duration("6/8"), 8)
        self.assertEqual(get_default_note_duration("4/4"), 8)
        self.assertEqual(get_default_note_duration("2/4"), 16)


class TestTranslateNotes(unittest.TestCase):

    def setUp(self):
        self.tc = TuneContext()
        self.tc.default_note_duration = get_default_note_duration("2/2")

    def tearDown(self):
        del self.tc

    def translate_and_test(self, abc_notes, expected_output):
        translate_notes(self.tc, abc_notes)
        self.assertEqual(self.tc.output, expected_output)

    def test_one_bar(self):
        abc_notes = "C2 D2 E2 F2"
        expected_output = ["c'4    d'4    e'4    f'4"]
        self.translate_and_test(abc_notes, expected_output)

    def test_empty_bar(self):
        abc_notes = ""
        expected_output = []
        self.translate_and_test(abc_notes, expected_output)

    def test_bar_starting_with_spaces(self):
        abc_notes = "   C2  D2   E2 F2  "
        expected_output = ["c'4    d'4    e'4    f'4"]
        self.translate_and_test(abc_notes, expected_output)

    def test_space_between_pitch_and_duration(self):
        abc_notes = "C2 D2 E2 F    2"
        expected_output = ["c'4    d'4    e'4    f'4"]
        self.translate_and_test(abc_notes, expected_output)

    def test_one_bar_with_eights_notes(self):
        abc_notes =  "CDEF GABc"
        expected_output = ["c'8    d'8    e'8    f'8    g'8    a'8    b'8    c''8"]
        self.translate_and_test(abc_notes, expected_output)

    def test_two_bars(self):
        abc_notes = "C2 D2 E2 F2 | G2 A2 B2 c2"
        expected_output = ["c'4    d'4    e'4    f'4    |"]
        expected_output.append("g'4    a'4    b'4    c''4")
        self.translate_and_test(abc_notes, expected_output)


class TestOutput(unittest.TestCase):

#    def test_hello_world(self):
#        # A very basic (eventually) syntaxely correct example:
#        # title, composer, common time
#        convert("regression/hello_world.abc",
#                       "regression-out/hello_world.ly")
#        self.assert_(filecmp.cmp("regression-out/hello_world.ly",
#                                 "regression-ref/hello_world.ly"))

    def test_hello_world_reel(self):
        # Check that the rythm/meter field is written
        # Check the "cut time" meter/time signature
        convert("regression/hello_world_reel.abc",
                       "regression-out/hello_world_reel.ly")
        self.assert_(filecmp.cmp("regression-out/hello_world_reel.ly",
                                 "regression-ref/hello_world_reel.ly"))

    def test_hello_world_empty_rythm(self):
        # Check that a blank rythm does not generate a meter field
        convert("regression/hello_world_empty_rythm.abc",
                       "regression-out/hello_world_empty_rythm.ly")
        self.assert_(filecmp.cmp("regression-out/hello_world_empty_rythm.ly",
                                 "regression-ref/hello_world_empty_rythm.ly"))

    def test_c_major(self):
        # The C major scale
        test = "regression/c_major.abc"
        out = "regression-out/c_major.ly"
        ref = "regression-ref/c_major.ly"

        convert(test, out)
        self.assert_(filecmp.cmp(out, ref),
                     "Files " + out + " and " + ref + " differ")

if __name__ == '__main__':
    unittest.main()
