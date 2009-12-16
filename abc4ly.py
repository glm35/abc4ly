#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function
import string

# ------------------------------------------------------------------------
#     Read and process the input file
# ------------------------------------------------------------------------

def read_info_line(line, header):
    raw_field = line[2:] # Remove the leading "T:" or so
    # Remove leading/trailing spaces, and substititue any occurence
    # of more than one space by just one space
    nice_field = string.join(raw_field.split(), " ")
    if line[0] == 'T':
        if header['title'] == "":
            header['title'] = nice_field
    elif line[0] == 'C':
        header['composer'] = nice_field
    elif line[0] == 'R':
        header['rythm'] = nice_field
    elif line[0] == 'M':
        header['meter'] = nice_field

def read_line(line, header):
    if line[0] in string.ascii_uppercase and line[1] == ":":
        read_info_line(line, header)
    # Comments (lines starting with '%') and empty lines are silently
    # ignored

def convert(abc_filename, ly_filename):
    header = {'title':'', 'composer':'', 'rythm':'', 'meter':''}
    with open(abc_filename, 'r') as abc_file:
        for line in abc_file.readlines():
            read_line(line, header)

        if ly_filename == '':
            return header

        with open(ly_filename, 'w') as ly_file:
            # Warning: with format(), curly braces must be escaped by
            # doubling them!
            ly_file.write(r'''\version "2.12.2"''' "\n")
            write_header(ly_file, header)
            ly_file.write(r'''
melody = \relative c' {
  \clef treble
  \key c \major
''')
            write_time_signature(ly_file, header['meter'])
            ly_file.write(r'''
  a4 b c d
}

\score {
  \new Staff \melody
  \layout { }
  \midi { }
}
''')
    return header

def write_header(ly_file, header):
    ly_file.write("\n" r'''\header {''' "\n")
    ly_file.write('  title = "{0}"\n'.format(header['title']))
    ly_file.write('  composer = "{0}"\n'.format(header['composer']))
    if header['rythm'] <> "":
        ly_file.write('  meter = "{0}"\n'.format(header['rythm']))
    ly_file.write("}\n")

# Returns True if "char_string" contains only digits
def only_digits(char_string):
    for char in list(char_string):
        if string.digits.find(char) == -1:
            return False
    return True

def write_time_signature(ly_file, meter):
    if meter == "C":
        time_signature = "4/4"
    elif meter == "C|":
        time_signature = "2/2"
    else:
        meter_tab = meter.split("/")
        for i in range(len(meter_tab)):
            meter_tab[i].strip()
        if len(meter_tab) != 2 or \
                not only_digits(meter_tab[0]) or \
                not only_digits(meter_tab[1]):
            raise Exception
        time_signature = string.join(meter_tab, "/")
    ly_file.write(r'''  \time {0}'''.format(time_signature) + "\n")
