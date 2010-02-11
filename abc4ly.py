#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function
import string
import sys
import math

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

        self.output = []


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

# ------------------------------------------------------------------------
#     Music computing stuff
# ------------------------------------------------------------------------

mc_modes = [ "ionian", "dorian", "phrygian", "lydian", "mixolydian",
             "aeolian", "minor", "locrian" ]

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
        tc.key_signature = translate_key_signature(line)
        tc.pitch_dico = create_pitch_dico(tc.key_signature)

def read_line(tc, line):
    print("[rl] line: +", line, "+")
    if line[0] in string.ascii_uppercase and line[1] == ":":
        read_info_line(tc, line)
    elif line.isspace() or line.lstrip()[0] == "%":
        # Silently ignore comments (lines starting with '%') and empty lines
        pass
    else:
        print("translating +" + line + "+")
        translate_notes(tc, line)
    print("[rl] tc.output:")
    print(tc.output)
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

def translate_key_signature(abc_key_signature):
    # Strip the leading "K:", remove any space, and substititue any
    # occurence of more than one space by just one space
    ks = abc_key_signature[2:]
    ks = string.join(ks.split(), "")
    pitch = ""
    alteration = ""
    mode = "major"

    state = "pitch"

    if len(ks) == 0:
        raise AbcSyntaxError

    while len(ks) != 0:

        if state == "pitch":
            # The first char should be the pitch
            pitch = ks[0].lower()
            if not pitch in "cdefgab":
                raise AbcSyntaxError
            ks = ks[1:]
            state = "alteration"

        elif state == "alteration":
            # Then optional alteration (sharp or flat)
            if ks[0] == "#":
                alteration = "is"
                ks = ks[1:]
            elif ks[0] == "b":
                alteration = "es"
                ks = ks[1:]
            state = "mode"

        elif state == "mode":
            # Then optional mode
            if ks == "m":
                mode = "minor"
            elif len(ks) < 3:
                raise AbcSyntaxError
            else:
                ks = ks.lower()
                mode = ""
                for m in mc_modes:
                    if m[0:3] == ks[0:3]:
                        mode = m
                        break
                if mode == "":
                    raise AbcSyntaxError

            # Forget the rest
            break

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
    bars = [ '|:', ':|', '|' ] # longest first, please
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
            note.clear()
            state = start_state

        elif state == "bar":
            bar = get_bar(al)
            al = al[len(bar):]
            e.colno += len(bar)

            if bar == "|:":
                tc.output.append("\repeat volta 2 {")
                tc.indent_level += 1
            elif bar == ":|":
                tc.output.append("    " * tc.indent_level + ly_line)
                tc.output.append("}")
                tc.indent_level -= 1
            elif bar == "|":
                tc.output.append("    " * tc.indent_level + ly_line + " |")

            if bar != "":
                ly_line = ""
                first_note = True

            state = "accidental"

        elif state == "accidental":
            abc_acc = al[0]
            acc_dico = {"^":"is", "_":"es", "=":"nat"}
            if abc_acc in acc_dico.keys():
                note.accidental = acc_dico[abc_acc]
                al = al[1:]
                e.colno += 1
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
            state = "duration"

        elif state == "duration":
            lm = get_leading_digits(al)
            if lm != "":
                if lm[0] == '/':
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
                else:
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
            # Else use default note length
            state = "done"

            # d+0,5d=2n
            # 1.5d = 2n

    if ly_line != "":
        tc.output.append("    " * tc.indent_level + ly_line)

# ------------------------------------------------------------------------
#     The main program
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

    if ly_filename == '':
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

        print("tc output:")
        print(tc.output)
        ly_file.write("\n")
        for line in tc.output:
            # First, we must escape the special caracters (such as "\r")
            # that can occur in some lilypond commands (such as
            # "\repeat"). To do this, we use the canonical
            # representation of the string and we remove the leading and
            # trailing quotes
            line = repr(line)
            line = line[1:len(line)-1]

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

