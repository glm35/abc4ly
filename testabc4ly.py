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


class TestMusicComputer(unittest.TestCase):

    def setUp(self):
        self.dico = {'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd',
                     'e': 'e', 'f': 'f', 'g': 'g'}

    def test_get_relative_major_scale_sharp(self):
        # A selection of modes widely used for Irish music
        self.assert_('c' == get_relative_major_scale('c', 'major'))
        self.assert_('c' == get_relative_major_scale('a', 'minor'))
        self.assert_('d' == get_relative_major_scale('b', 'minor'))
        self.assert_('d' == get_relative_major_scale('e', 'dorian'))
        self.assert_('d' == get_relative_major_scale('a', 'mixolydian'))
        self.assert_('g' == get_relative_major_scale('e', 'minor'))
        self.assert_('g' == get_relative_major_scale('d', 'mixolydian'))
        self.assert_('a' == get_relative_major_scale('fis', 'minor'))

    def test_get_relative_major_scale_flat(self):
        self.assert_('f' == get_relative_major_scale('f', 'major'))
        self.assert_('ees' == get_relative_major_scale('ees', 'major'))
        self.assert_('bes' == get_relative_major_scale('g', 'minor'))

    def test_pitch_dico_cmaj(self):
        self.assert_(self.dico == create_pitch_dico("\key c \major"))

    def test_pitch_dico_dmaj(self):
        self.dico['f'] = 'fis'
        self.dico['c'] = 'cis'
        self.assert_(self.dico == create_pitch_dico("\key d \major"))

    def test_pitch_dico_cismaj(self):
        for n in "fcgdaeb":
            self.dico[n] = n + 'is'
        self.assert_(self.dico == create_pitch_dico("\key cis \major"))

    def test_pitch_dico_besmaj(self):
        self.dico['b'] = 'bes'
        self.dico['e'] = 'ees'
        self.assert_(self.dico == create_pitch_dico("\key bes \major"))

    def test_pitch_dico_fmaj(self):
        self.dico['b'] = 'bes'
        self.assert_(self.dico == create_pitch_dico("\key f \major"))

    def test_pitch_dico_gesmaj(self):
        for f in "beadgc":
            self.dico[f] = f + 'es'
        self.assert_(self.dico == create_pitch_dico("\key ges \major"))

#    def test_pitch_dico_cesmaj(self):
#        for f in "beadgcf":
#            self.dico[f] = f + 'es'
#        self.assert_(self.dico == create_pitch_dico("\key ces \major"))


# Base class to test the  translate_notes() function

class TestTranslateNotes(unittest.TestCase):

    def setUp(self):
        self.tc = TuneContext()
        self.tc.default_note_duration = get_default_note_duration("2/2")

    def tearDown(self):
        del self.tc

    def translate_and_test(self, abc_notes, expected_output):
        translate_notes(self.tc, abc_notes)
        self.assertEqual(expected_output, self.tc.output)

    def translate_and_check_exception(self, abc_notes, exception_text):
        try:
            translate_notes(self.tc, abc_notes)
        except (AbcSyntaxError), e:
            print e.__str__()
            self.assertEqual(e.__str__(), exception_text)
        else:
            self.assert_(False)


class TestTranslateNotesBasic(TestTranslateNotes):

    def test_one_bar(self):
        abc_notes = "C2 D2 E2 F2"
        expected_output = ["c'4 d'4 e'4 f'4"]
        self.translate_and_test(abc_notes, expected_output)

    def test_empty_bar(self):
        abc_notes = ""
        expected_output = []
        self.translate_and_test(abc_notes, expected_output)

    def test_bar_starting_with_spaces(self):
        abc_notes = "   C2  D2   E2 F2  "
        expected_output = ["c'4 d'4 e'4 f'4"]
        self.translate_and_test(abc_notes, expected_output)

    def test_space_between_pitch_and_duration(self):
        abc_notes = "C2 D2 E2 F    2"
        expected_output = ["c'4 d'4 e'4 f'4"]
        self.translate_and_test(abc_notes, expected_output)

    def test_one_bar_with_eights_notes(self):
        abc_notes =  "CDEF GABc"
        expected_output = ["c'8 d'8 e'8 f'8 g'8 a'8 b'8 c''8"]
        self.translate_and_test(abc_notes, expected_output)


# Test the translation of the structure: bar delimiters, repetitions

class TestTranslateNotesStructure(TestTranslateNotes):

    def test_two_bars(self):
        abc_notes = "C2 D2 E2 F2 | G2 A2 B2 c2"
        expected_output = ["c'4 d'4 e'4 f'4 |"]
        expected_output.append("g'4 a'4 b'4 c''4")
        self.translate_and_test(abc_notes, expected_output)

    def test_empty_note_line(self):
        abc_notes = ""
        expected_output = []
        self.translate_and_test(abc_notes, expected_output)

    def test_one_bar_repeat(self):
        abc_notes =  "|: cdef gabc' :|"
        expected_output = ["\repeat volta 2 {",
                           "    c''8 d''8 e''8 f''8 g''8 a''8 b''8 c'''8",
                           "}"]
        self.translate_and_test(abc_notes, expected_output)

    def test_two_bars_repeat(self):
        abc_notes =  "|: cdef gabc' | cedf gbac' :|"
        expected_output = ["\repeat volta 2 {",
                           "    c''8 d''8 e''8 f''8 g''8 a''8 b''8 c'''8 |",
                           "    c''8 e''8 d''8 f''8 g''8 b''8 a''8 c'''8",
                           "}"]
        self.translate_and_test(abc_notes, expected_output)


class TestTranslateNotesKeys(TestTranslateNotes):

    def test_lower_c_major(self):
        abc_notes =  "C,D,E,F, G,A,B,C"
        expected_output = ["c8 d8 e8 f8 g8 a8 b8 c'8"]
        self.translate_and_test(abc_notes, expected_output)

    def test_upper_c_major(self):
        abc_notes =  "cdef gabc'"
        expected_output = ["c''8 d''8 e''8 f''8 g''8 a''8 b''8 c'''8"]
        self.translate_and_test(abc_notes, expected_output)

    def test_e_minor(self):
        read_info_line(self.tc, "M:6/8")
        read_info_line(self.tc, "K:Em")
        abc_notes = "GEF G2A"
        expected_output = ["g'8 e'8 fis'8 g'4 a'8"]
        self.translate_and_test(abc_notes, expected_output)

    def test_d_major(self):
        read_info_line(self.tc, "K:D")
        abc_notes =  "DEFG ABcd"
        expected_output = ["d'8 e'8 fis'8 g'8 a'8 b'8 cis''8 d''8"]
        self.translate_and_test(abc_notes, expected_output)


# Test notes longer than the default note length

class TestTranslateNotesLongerDuration(TestTranslateNotes):

    def test_quarter_notes(self):
        read_info_line(self.tc, "M:4/4")
        abc_notes = "C2 D2 E2 F2"
        expected_output = ["c'4 d'4 e'4 f'4"]
        self.translate_and_test(abc_notes, expected_output)

    def test_half_notes(self):
        read_info_line(self.tc, "M:4/4")
        abc_notes = "C4 D4"
        expected_output = ["c'2 d'2"]
        self.translate_and_test(abc_notes, expected_output)

    def test_whole_notes(self):
        read_info_line(self.tc, "M:4/4")
        abc_notes = "C8"
        expected_output = ["c'1"]
        self.translate_and_test(abc_notes, expected_output)

    def test_dotted_quarter_notes(self):
        read_info_line(self.tc, "M:6/8")
        abc_notes = "CDE C3"
        expected_output = ["c'8 d'8 e'8 c'4."]
        self.translate_and_test(abc_notes, expected_output)

    def test_dotted_half_notes(self):
        read_info_line(self.tc, "M:2/2")
        abc_notes = "C6 D2"
        expected_output = ["c'2. d'4"]
        self.translate_and_test(abc_notes, expected_output)

    def test_unhandled_multiplier(self):
        abc_notes = "C5 D3"
        self.translate_and_check_exception(abc_notes, """In "", line 1, column 1:
C5 D3
 ^
 Unhandled duration multiplier""")


# Test notes shorter than the default note length

class TestTranslateNotesShorterDuration(TestTranslateNotes):

    def test_sixteenth_notes_shorthand_representation(self):
        read_info_line(self.tc, "M:4/4")
        abc_notes = "C/D/E/D/ C/D/E/D/ C/D/E/D/ C/D/C"
        expected_output = ["c'16 d'16 e'16 d'16 " "c'16 d'16 e'16 d'16 "
                           "c'16 d'16 e'16 d'16 " "c'16 d'16 e'16 c'8"]
        self.translate_and_test(abc_notes, expected_output)


class TestTranslateNotesSyntaxError(TestTranslateNotes):

    def test_octaver_error_down(self):
        abc_notes = "c,D,E,F, G,A,B,C"
        self.translate_and_check_exception(abc_notes, """In "", line 1, column 1:
c,D,E,F, G,A,B,C
 ^
 'c,' is not syntactically correct""")

    def test_octaver_error_up(self):
        abc_notes = "C'D,E,F, G,A,B,C"
        self.translate_and_check_exception(abc_notes, """In "", line 1, column 1:
C'D,E,F, G,A,B,C
 ^
 "C'" is not syntactically correct""")

    def test_not_a_pitch(self):
        abc_notes = "cdef XYZK"
        self.translate_and_check_exception(abc_notes, """In "", line 1, column 5:
cdef XYZK
     ^
     'X' is not a pitch""")

    def test_not_a_pitch_leading_spaces(self):
        abc_notes = "   cdef XYZK"
        self.translate_and_check_exception(abc_notes, """In "", line 1, column 8:
   cdef XYZK
        ^
        'X' is not a pitch""")


class TestOutput(unittest.TestCase):

    def check_output(self, basename):
        test = "regression/" + basename + ".abc"
        out = "regression-out/" + basename + ".ly"
        ref = "regression-ref/" + basename + ".ly"
        convert(test, out)
        self.assert_(filecmp.cmp(ref, out),
                     "Files " + ref + " and " + out + " differ")

    def test_c_major(self):
        # The C major scale
        self.check_output("c_major")

    def test_hello_world(self):
        # A very basic (eventually) syntaxely correct example:
        # title, composer, common time
        self.check_output("hello_world")

    def test_hello_world_reel(self):
        # Check that the rythm/meter (abc/ly) field is written
        self.check_output("hello_world_reel")

    def test_hello_world_empty_rythm(self):
        # Check that a blank rythm (abc) does not generate a meter (ly) field
        self.check_output("hello_world_empty_rythm")

    def test_hello_repeated(self):
        self.check_output("hello_repeated")

    def test_brid_harper_s(self):
        self.check_output("brid_harper_s")

    def xtest_yellow_tinker(self):
        self.check_output("yellow_tinker")


if __name__ == '__main__':
    unittest.main()

#suite = unittest.TestLoader().loadTestsFromTestCase(TestTranslateNotesDuration)
#unittest.TextTestRunner(verbosity=2).run(suite)

