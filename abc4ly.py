#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function
import string
import sys
import math
import optparse
import copy


# ------------------------------------------------------------------------
#     Exceptions
# ------------------------------------------------------------------------

class AbcSyntaxError(Exception):
    def __init__(self):
        self.what = ""
        self.filename = ""
        self.abc_line = ""
        self.lineno = 0 # line count starts at 1 (idem Emacs)
        self.colno = 0  # column count starts at 0 (idem Emacs)

    def __str__(self):
        return """In "{0}", line {1}, column {2}:
{3}
{4}^
{4}{5}""".format(self.filename, self.lineno, self.colno,
                 self.abc_line,
                 " " * self.colno, self.what)

# ------------------------------------------------------------------------
#     Tune context
# ------------------------------------------------------------------------

class TuneContext():
    def __init__(self):
        self.filename = ""
        self.lineno = 1

        self.title = ""
        self.composer = ""
        self.rythm = ""
        self.meter = ""
        self.key_signature = ""
        self.pitch_dico = create_pitch_dico("\key c \major")

        self.default_note_duration = 0

        self.indent_level = 0
        self.alternative = 0
        self.prev_note = None
        self.in_triplet = False
        self.triplet_count = 0
        self.in_broken_rythm = False

        self.output = []

    def dump_bar(self, notes, abc_bar):
        if abc_bar == "||":
            bar_glyph = r'\bar "||"'
        elif abc_bar == "|]":
            bar_glyph = r'\bar "|."'
        else:
            bar_glyph = "|"
        self.output.append("    " * self.indent_level + notes + " " + bar_glyph)

    def dump_note_block(self, notes):
        self.output.append("    " * self.indent_level + "{ " + notes + " }")

    def open_repeat(self):
        self.output.append("\repeat volta 2 {")
        self.indent_level += 1

    def close_repeat(self, ly_line):
        self.output.append("    " * self.indent_level + ly_line)
        self.output.append("}")
        self.indent_level -= 1

    def begin_alternative_1(self):
        self.output.append(r"\alternative {")
        self.alternative = 1
        self.indent_level += 1
        # Remark: No way not to use raw strings with this crazy "\a"
    
    def begin_alternative_2(self):
        self.alternative = 2

    def end_alternative(self):
        self.output.append("}")
        self.indent_level -= 1
        self.alternative = 0


# ------------------------------------------------------------------------
#     The logical representation of a LilyPond note
# ------------------------------------------------------------------------

class Note():
    def __init__(self):
        self.clear()

    def clear(self):
        self.accidental = ""
        self.pitch = ""
        self.octaver = ""
        self.duration = ""
        self.dotted = ""
        self.tied = ""
        self.chord = ""

    def same_pitch(self, note):
        return (self.pitch == note.pitch
                and self.octaver == note.octaver)

        # Remark: self.accidental only stores explicit accidentals set
        # with _, ^ and = in the abc file, and not diatonic
        # accidentals. same_pitch() is intended for being called when
        # explicit and implicit accidentals have been included into
        # self.pitch. So self.accidental is not used in the comparison
        # of note pitches.


# ------------------------------------------------------------------------
#     Music computing stuff
# ------------------------------------------------------------------------

mc_modes = [ "major", "ionian", "dorian", "phrygian", "lydian",
             "mixolydian", "aeolian", "minor", "locrian" ]

# Number of semi-tones between the fundamental note of a mode and the
# fundamental note of its relative major key.  (e.g. there are 9
# semi-tones between the c in C major and the a in A minor)
mc_mode_offsets = {"major":0, "ionian":0, "dorian":2, "phrygian":4, "lydian":5,
                   "mixolydian":7, "aeolian":9, "minor":9, "locrian":11}

mc_sharp_chromatic_scale = ['c', 'cis', 'd', 'dis', 'e', 'f', 'fis', 'g',
                             'gis', 'a', 'ais', 'b']
mc_nsharp_dico = {'g':1, 'd':2, 'a':3, 'e':4, 'b':5, 'fis':6, 'cis':7}
mc_sharp_order = "fcgdaeb"

mc_flat_chromatic_scale = ['c', 'des', 'd', 'ees', 'e', 'f', 'ges', 'g',
                             'aes', 'a', 'bes', 'b']
mc_nflat_dico = {'f':1, 'bes':2, 'ees':3, 'aes':4, 'des':5, 'ges':6, 'ces':7}
mc_flat_order = "beadgcf"

# ------------------------------------------------------------------------
#     Read and process the input file
# ------------------------------------------------------------------------

def read_info_line(tc, line):
    raw_field = line[2:] # Remove the leading "T:" or so
    # Remove leading/trailing spaces, and substititue any occurence
    # of more than one space by just one space
    nice_field = string.join(raw_field.split(), " ")
    if line[0] == 'T':
        if tc.title == "":
            tc.title = nice_field
    elif line[0] == 'C':
        tc.composer = nice_field
    elif line[0] == 'R':
        tc.rythm = nice_field
    elif line[0] == 'M':
        tc.meter = normalize_time_signature(nice_field)
        tc.default_note_duration = get_default_note_duration(tc.meter)
    elif line[0] == 'K':
        tc.key_signature = translate_key_signature(tc, line)
        tc.pitch_dico = create_pitch_dico(tc.key_signature)

def read_line(tc, line):
    if line[0] in string.ascii_uppercase and line[1] == ":":
        read_info_line(tc, line)
    elif line.isspace() or line.lstrip()[0] == "%":
        # Silently ignore comments (lines starting with '%') and empty lines
        pass
    else:
        translate_notes(tc, line)
    tc.lineno += 1

# ------------------------------------------------------------------------
#     Write the lilypond output
# ------------------------------------------------------------------------

def write_header(tc, ly_file):
    ly_file.write("\n" r'''\header {''' "\n")
    ly_file.write('    title = "{0}"\n'.format(tc.title))
    if tc.composer <>"":
        ly_file.write('    composer = "{0}"\n'.format(tc.composer))
    if tc.rythm <> "":
        ly_file.write('    meter = "{0}"\n'.format(tc.rythm))
    ly_file.write("}\n")

def normalize_time_signature(meter):
    if meter == "C":
        time_signature = "4/4"
    elif meter == "C|":
        time_signature = "2/2"
    else:
        meter_tab = meter.split("/")
        for i in range(len(meter_tab)):
            meter_tab[i] = meter_tab[i].strip()
        if len(meter_tab) != 2 or \
                not meter_tab[0].isdigit() or \
                not meter_tab[1].isdigit():
            raise AbcSyntaxError
        time_signature = string.join(meter_tab, "/")
    return time_signature

def write_time_signature(ly_file, meter):
    time_signature = normalize_time_signature(meter)
    ly_file.write(r'''    \time {0}'''.format(time_signature) + "\n")

# Translate a key signature in ABC format to a key signature in lilypond
# format. Currently, this function only understands a key signature in
# the format: pitch (one letter) + (opt) # or b + (opt) mode
#
# input: abc_key_signature: contents of the "K:" line with the "K:" prefix

def translate_key_signature(tc, abc_key_signature):
    # Prepare an exception (just in case)
    e = AbcSyntaxError()
    e.filename = tc.filename
    e.abc_line = abc_key_signature.rstrip()
    e.lineno = tc.lineno
    e.colno = 0

    # Strip the leading "K:" and the trailing white spaces
    ks = abc_key_signature[2:]
    e.colno += 2
    ks = ks.rstrip()

    pitch = ""
    alteration = ""
    mode = "major"

    state = "pitch"

    while True:

        len_before = len(ks)
        ks = ks.lstrip()
        e.colno += len_before - len(ks)
        if len(ks) == 0:
            break

        if state == "pitch":
            # The first char should be the pitch
            pitch = ks[0].lower()
            if not pitch in "cdefgab":
                e.what = "Invalid pitch"
                raise e
            ks = ks[1:]
            e.colno += 1
            state = "alteration"

        elif state == "alteration":
            # Then optional alteration (sharp or flat)
            alterations = {"#":"is", "b":"es"}
            if ks[0] in alterations.keys():
                alteration = alterations[ks[0]]
                ks = ks[1:]
                e.colno += 1
            state = "mode"

        elif state == "mode":
            # Then optional mode
            if ks == "m":
                mode = "minor"
            else:
                mode = ""
                if len(ks) >= 3:
                    ks = ks.lower()
                    for m in mc_modes:
                        if m[0:3] == ks[0:3]:
                            mode = m
                            break
                if mode == "":
                    e.what = "Invalid mode"
                    raise e

            # Forget the rest
            break

    if state == "pitch":
        e.what = "Empty key signature"
        raise e

    lily_signature = "\key " + pitch + alteration + " " + "\\" + mode
    return lily_signature

def get_relative_major_scale(key, mode):
    mode_interval = mc_mode_offsets[mode]
    n_semi_tones_to_fundamental = 12 - mode_interval

    try:
        mode_chrom_index = mc_sharp_chromatic_scale.index(key)
        system = 'sharp'
    except:
        mode_chrom_index = mc_flat_chromatic_scale.index(key)
        system = 'flat'

    major_key_index = mode_chrom_index + n_semi_tones_to_fundamental
    if major_key_index >= 12:
        major_key_index -= 12

    if system == 'sharp':
        maj_key = mc_sharp_chromatic_scale[major_key_index]
        if not maj_key in mc_nsharp_dico.keys():
            system = 'flat'
    if system == 'flat':
        maj_key = mc_flat_chromatic_scale[major_key_index]

    return maj_key

# Create a dictionary that contains the pitch alterations (sharps,
# flats) implied by the key signature.

def create_pitch_dico(ly_key_signature):
    # example: ly_key_signature = "\key c \major"
    (foo, key, mode) = ly_key_signature.split()
    mode = mode[1:]
    pitch_dico = {}

    key = get_relative_major_scale(key, mode)

    for note in "cdefgab":
        pitch_dico[note] = note

    if key in mc_nsharp_dico.keys():
        nsharp = mc_nsharp_dico[key]
        sharps = mc_sharp_order[0:nsharp]
        for pitch in sharps:
            pitch_dico[pitch] = pitch + "is"
    elif key in mc_nflat_dico.keys():
        nflat = mc_nflat_dico[key]
        flats = mc_flat_order[0:nflat]
        for pitch in flats:
            pitch_dico[pitch] = pitch + "es"

    return pitch_dico

def get_leading_digits(string):
    leading_digits = ""
    i = 0
    for char in string:
        if (i == 0 and char == '/') or char.isdigit():
            leading_digits += char
            i += 1
        else:
            break
    return leading_digits

# Given the time signature as a fraction (e.g. "6/8" or "4/4"), compute
# the default note length in lilypond format

def get_default_note_duration(time_signature):
    ts_tab = time_signature.split("/")
    num = float(ts_tab[0])
    den = float(ts_tab[1])
    if num / den < 0.75:
        return 16
    else:
        return 8

# Given a snippet of ABC music, try to recognize a repeat or bar pattern

def get_bar(abc_snippet):
    bars = [ ':|2', #'|[1', '|[2',
             '|1', '|:', ':|', '||', '|]', '::', '[2', #'|2', '[|'
             '|' ] # longest first, please
    bar = ""

    for b in bars:
        if len(abc_snippet) >= len(b) and abc_snippet[0:len(b)] == b:
            bar = b
            break

    return bar
        

# Given a line of ABC music, translate the line to lilypond

def translate_notes(tc, abc_line):
    # Prepare an exception (just in case)
    e = AbcSyntaxError()
    e.filename = tc.filename
    e.abc_line = abc_line.rstrip()
    e.lineno = tc.lineno
    e.colno = 0

    pitches = "abcdefgABCDEFG"

    al = abc_line
    start_state = "bar"
    state = start_state
    ly_line = ""
    first_note = True
    note = Note()

    while len(al) != 0 or state != start_state:

        len_before = len(al)
        al = al.lstrip()
        e.colno += len_before - len(al)

        if len(al) == 0 or state == "done":
            # Dump note
            if not first_note:
                ly_line += " "
            else:
                first_note = False
            ly_line += note.pitch + note.octaver + str(note.duration) + note.dotted
            if note.tied:
                ly_line += " ~"
            if note.chord != "":
                ly_line += ' ^"{0}"'.format(note.chord)
            if tc.in_triplet and tc.triplet_count == 3:
                ly_line += " }"
                tc.in_triplet = False
            tc.prev_note = copy.copy(note)
            note.clear()
            state = start_state

        elif state == "bar":
            bar = get_bar(al)
            al = al[len(bar):]
            e.colno += len(bar)

            if bar == "|:":
                tc.open_repeat()
            elif bar == ":|":
                if tc.alternative == 0:
                    tc.close_repeat(ly_line)
                elif tc.alternative == 1:
                    tc.dump_note_block(ly_line)
            elif bar == "::":
                tc.close_repeat(ly_line)
                tc.open_repeat()
            elif bar == "|1":
                tc.close_repeat(ly_line)
                tc.begin_alternative_1()
            elif bar == ":|2":
                tc.dump_note_block(ly_line)
                tc.begin_alternative_2()
            elif bar == "[2":
                tc.begin_alternative_2()
            elif bar == "|" or bar == "||" or bar == "|]":
                if tc.alternative == 2:
                    tc.dump_note_block(ly_line)
                    tc.end_alternative()
                else:
                    tc.dump_bar(ly_line, bar)

            if bar != "":
                ly_line = ""
                first_note = True
            else:
                state = "chord"

        elif state == "chord":
            if al[0] == '"':
                al = al[1:]
                e.colno += 1
                while len(al) >= 1 and al[0] != '"':
                    note.chord += al[0]
                    al = al[1:]
                    e.colno += 1
                if len(al) >= 1 and al[0] == '"':
                    al = al[1:]
                    e.colno += 1
                else:
                    e.what = "Missing the guitar chord closing inverted commas"
                    raise e
            state = "triplet"

        elif state == "triplet":
            # My Own Interpretation: a chord change can occur during a
            # triplet. But a chord change on the first note of a triplet
            # should be written before the triplet marker.
            if len(al) >= 2 and al[0:2] == "(3":
                al = al[2:]
                e.colno += 2
                ly_line += "\times 2/3 { "
                tc.in_triplet = True
                tc.triplet_count = 0
            state = "accidental"

        elif state == "accidental":
            acc_dico = {"^":"is", "^^":"isis", "_":"es", "__":"eses", "=":"nat"}
            abc_acc = ""
            if len(al) >= 2 and al[0:2] in acc_dico.keys():
                abc_acc = al[0:2]
            elif al[0] in acc_dico.keys():
                abc_acc = al[0]
            if abc_acc != "":
                note.accidental = acc_dico[abc_acc]
                al = al[len(abc_acc):]
                e.colno += len(abc_acc)
            state = "rest"

        elif state == "rest":
            if al[0] == "z":
                note.pitch = "r"
                note.duration = tc.default_note_duration
                al = al[1:]
                e.colno += 1
                if tc.in_triplet:
                    tc.triplet_count += 1
                state = "check_ties"
            else:
                state = "pitch"
        
        elif state == "pitch":
            abc_pitch = al[0]
            if not abc_pitch in pitches:
                e.what = "'{0}' is not a pitch".format(abc_pitch)
                raise e
            al = al[1:]
            e.colno += 1
            if note.accidental == "":
                note.pitch = tc.pitch_dico[abc_pitch.lower()]
            else:
                note.pitch = abc_pitch.lower()
                if note.accidental != "nat":
                    note.pitch += note.accidental
            note.duration = tc.default_note_duration
            if abc_pitch.lower() == abc_pitch:
                note.octaver = "''"
            else:
                note.octaver = "'"
            if tc.in_triplet:
                tc.triplet_count += 1
            state = "octaver"

        elif state == "octaver":
            # Look for "," or "'"
            octaver = al[0]
            if octaver == ",":
                if note.octaver == "''":
                    # "c," etc is an invalid ABC construct
                    e.what = "'{0}{1}' is not syntactically correct".format(abc_pitch, octaver)
                    raise e
                note.octaver = ""
            elif octaver == "'":
                if note.octaver == "'":
                    # "C'" etc is an invalid ABC construct
                    e.what = '"{0}{1}" is not syntactically correct'.format(abc_pitch, octaver)
                    raise e
                note.octaver += "'"
            if octaver == "'" or octaver == ",":
                al = al[1:]
                e.colno += 1
            state = "check_ties"

        elif state == "check_ties":
            # Check that two tied notes have the same pitch
            if tc.prev_note != None and tc.prev_note.tied == True:
                if not note.same_pitch(tc.prev_note):
                    e.what = "The tied notes do not have the same pitch"
                    raise e
            state = "duration"

        elif state == "duration":
            if al[0] == '>':
                note.dotted = "."
                tc.in_broken_rythm = True
                al = al[1:]
                e.colno += 1
                state = "tie"
            elif tc.in_broken_rythm:
                note.duration *= 2
                tc.in_broken_rythm = False
                state = "tie"
            else:
                state = "duration_multiplier"

        elif state == "duration_multiplier":
            lm = get_leading_digits(al)
            if lm != "" and lm[0] != '/':
                abc_duration = int(lm)
                if abc_duration % 1.5 == 0:
                    note.duration /= int(abc_duration / 1.5)
                    note.dotted = "."
                elif abc_duration % 2 == 0:
                    note.duration /= abc_duration
                else:
                    e.what = "Unhandled duration multiplier"
                    raise e
                al = al[len(lm):]
                e.colno += len(lm)
            state = "duration_divider"

        elif state == "duration_divider":
            lm = get_leading_digits(al)
            if lm != "" and lm[0] == '/':
                if len(lm) == 1:
                    note.duration *= 2
                else:
                    divisor = int(lm[1:])
                    exponent = math.log(divisor, 2)
                    if exponent != 0 and int(exponent) == exponent:
                        # divisor is a power of 2
                        note.duration *= divisor
                    else:
                        e.colno += 1 # pass the slash
                        e.what = "Invalid note duration divisor"
                        raise e
                al = al[len(lm):]
                e.colno += len(lm)
            # Else use default note length
            state = "tie"

        elif state == "tie":
            if al[0] == '-':
                al = al[1:]
                e.colno += 1
                note.tied = True
            state = "done"

    if ly_line != "":
        tc.output.append("    " * tc.indent_level + ly_line)


# ------------------------------------------------------------------------
#     The high-level conversion function
# ------------------------------------------------------------------------

def open_abc(abc_filename):
    abc_file = open(abc_filename, 'r')
    return abc_file

def convert(abc_filename, ly_filename):
    abc_file = open_abc(abc_filename)

    # Setup the context data

    tc = TuneContext()
    tc.filename = abc_filename

    # Parse the ABC file

    for line in abc_file.readlines():
        read_line(tc, line)

    if ly_filename == None or ly_filename == '':
        ly_file = sys.stdout
    else:
        ly_file = open(ly_filename, 'w')

    try:
        # Warning: with format(), curly braces must be escaped by
        # doubling them!
        ly_file.write(r'''\version "2.12.2"''' "\n")
        write_header(tc, ly_file)
        ly_file.write(r'''
melody = {
    \clef treble
''')
        ly_file.write("    " + tc.key_signature + "\n")
        write_time_signature(ly_file, tc.meter)

        ly_file.write("\n")
        for line in tc.output:
            # First, we must escape the special caracters (such as "\r")
            # that can occur in some lilypond commands (such as
            # "\repeat"). To do this, we use the canonical
            # representation of the string and we remove:
            # - the leading and quotes
            # - the spurious backslashes inserted when we mix chords
            #    with apostrophe
            # - the spurious backslash inserted when we use raw strings with "\a"
            line = repr(line)
            line = line[1:len(line)-1]
            line = line.replace("\\\'", "\'")
            line = line.replace("\\\\", "\\")

            # Then we can write the line safely...
            ly_file.write("    " + line + "\n")

        ly_file.write(r'''}

\score {
    \new Staff \melody
    \layout { }
    \midi { }
}
''')
    finally:
        if ly_file != sys.stdout:
            ly_file.close()

    return tc


# ------------------------------------------------------------------------
#     The main program
#
#     (not executed when abc4ly.py is imported: needed for unitary
#     tests)
# ------------------------------------------------------------------------

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-o", "--output", dest="filename",
                      help="write output to FILE (default: standard output)", metavar="FILE")
    (options, args) = parser.parse_args()
    convert(args[0], options.filename)
