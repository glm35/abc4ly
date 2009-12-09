#!/usr/bin/env python
# -*- coding:utf-8 -*-

import string

title = ""

def process_info_line(line):
    if line[0] == 'T':
        # Remove the leading "T:"
        tmp = line[2:]
        # Remove leading/trailing spaces, and substititue any occurence
        # of more than one space by just one space
        tmp = string.join(tmp.split(), " ")
        global title
        title = tmp

def process_line(line):
    if line[0] in string.ascii_uppercase and line[1] == ":":
        process_info_line(line)

def convert(abc_filename, ly_filename):
    with open(abc_filename, 'r') as abc_file:
        for line in abc_file.readlines():
            process_line(line)
