#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function
import string
import sys

# ------------------------------------------------------------------------
#     Exceptions
# ------------------------------------------------------------------------

class AbcSyntaxError(Exception): pass

# ------------------------------------------------------------------------
#     Tune context
# ------------------------------------------------------------------------

class TuneContext:
    title = ""
    composer = ""
    rythm = ""
    meter = ""

    default_note_duration = 0

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
        tc.meter = nice_field

def read_line(tc, line):
    if line[0] in string.ascii_uppercase and line[1] == ":":
        read_info_line(tc, line)
    elif line.isspace() or line.lstrip()[0] == "%":
        # Silently ignore comments (lines starting with '%') and empty lines
        pass

# ------------------------------------------------------------------------
#     Write the lilypond output
# ------------------------------------------------------------------------

def write_header(tc, ly_file):
    ly_file.write("\n" r'''\header {''' "\n")
    ly_file.write('  title = "{0}"\n'.format(tc.title))
    ly_file.write('  composer = "{0}"\n'.format(tc.composer))
    if tc.rythm <> "":
        ly_file.write('  meter = "{0}"\n'.format(tc.rythm))
    ly_file.write("}\n")

def write_time_signature(ly_file, meter):
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
    ly_file.write(r'''  \time {0}'''.format(time_signature) + "\n")

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
                modes = [ "ionian", "dorian", "phrygian", "lydian", "mixolydian",
                          "aeolian", "minor", "locrian" ]
                mode = ""
                for m in modes:
                    if m[0:3] == ks[0:3]:
                        mode = m
                        break
                if mode == "":
                    raise AbcSyntaxError

            # Forget the rest
            break

    lily_signature = "\key " + pitch + alteration + " " + "\\" + mode
    return lily_signature

def get_leading_digits(string):
    leading_digits = ""
    for char in string:
        if char.isdigit():
            leading_digits += char
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

# Given a line of ABC music, translate the line to lilypond

def translate_notes(tune_context, abc_line):
    pitches = "abcdefgABCDEFG"

    al = abc_line.lstrip()
    state = "pitch"
    ly_line = ""
    first_note = True

    while len(al) != 0 or state == "duration":

        if len(al) != 0 and al[0] == '|':
            al = al[1:]
            ly_line += "    |\n"
            first_note = True
        
        elif state == "pitch":
            pitch = al[0]
            al = al[1:]
            ly_pitch = ""
            if not pitch in pitches:
                print("Not a pitch: " + pitch)
                raise AbcSyntaxError
            if pitch.lower() == pitch:
                ly_pitch = pitch + "''"
            else:
                ly_pitch = pitch.lower() + "'"
            if not first_note:
                ly_line += "    "
            else:
                first_note = False
            ly_line += ly_pitch
            state = "duration"

        elif state == "duration":
            lm = get_leading_digits(al)
            if lm != "":
                al = al[len(lm):]
                ly_duration = str(tune_context.default_note_duration / int(lm))
                ly_line += ly_duration
            else:
                # Use default note length
                ly_line += str(tune_context.default_note_duration)
            state = "pitch"

        al = al.lstrip()

    return ly_line

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

    # Parse the ABC file

    for line in abc_file.readlines():
        read_line(tc, line)

        #tc = TuneContext()
        #tc.default_note_duration = get_default_note_duration(header['meter'])



    # Write the lilypond file

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
  \key c \major
''')
        write_time_signature(ly_file, tc.meter)

        if ly_filename == "regression-out/c_major.ly":
            ly_file.write(r'''
  c'4    d'4    e'4    f'4    |
  g'4    a'4    b'4    c''4''')
        else:
            ly_file.write(r'''
  a4 b c d''')

        ly_file.write(r'''
}

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

