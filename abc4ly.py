#!/usr/bin/env python
# -*- coding:utf-8 -*-

import string

title = ""
composer = ""
rythm = ""

# ------------------------------------------------------------------------
#     Read and process the input file
# ------------------------------------------------------------------------

def read_info_line(line):
    raw_field = line[2:] # Remove the leading "T:" or so
    # Remove leading/trailing spaces, and substititue any occurence
    # of more than one space by just one space
    nice_field = string.join(raw_field.split(), " ")
    if line[0] == 'T':
        global title
        if title == "":
            title = nice_field
    elif line[0] == 'C':
        global composer
        composer = nice_field
    elif line[0] == 'R':
        global rythm
        rythm = nice_field

def read_line(line):
    if line[0] in string.ascii_uppercase and line[1] == ":":
        read_info_line(line)
    # Comments (lines starting with '%') and empty lines are silently
    # ignored

def convert(abc_filename, ly_filename):
    with open(abc_filename, 'r') as abc_file:
        for line in abc_file.readlines():
            read_line(line)

        if ly_filename == '':
            return

        with open(ly_filename, 'w') as ly_file:
            print >> ly_file, r'''\version "2.12.2"

\header {
  title = "%s"
  composer = "%s"
}

melody = \relative c' {
  \clef treble
  \key c \major
  \time 4/4
  
  a4 b c d
}

\score {
  \new Staff \melody
  \layout { }
  \midi { }
}''' % (title, composer)
