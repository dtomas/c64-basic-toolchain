#!/usr/bin/env python

import re
import sys
from sys import stdin, stdout
import cStringIO

line_number = 1

labels = {}
consts = {}

CONST_RE = re.compile(
    r"^ *const *(?P<name>[a-zA-Z_]+) *= *(?P<value>.+) *$"
)


buf = cStringIO.StringIO()

for line in sys.stdin.readlines():
    quotes = False
    line = line.lstrip(' \t')
    if line == '\n':
        continue # empty line
    if line.startswith('rem') and line[3] != '`':
        continue # comment, but no compiler directive
    if line.startswith('#'):
        continue # comment

    if line.endswith(':\n'):
        # label
        label = line[:-2]
        labels[label] = line_number
    elif line.startswith('const'):
        match = CONST_RE.match(line)
        if match is None:
            raise SyntaxError("Invalid const definition: %s" % line)
        groups = match.groupdict()
        parts = line.split(' ')
        name = groups['name']
        value = groups['value']
        consts[name] = value
    else:
        buf.write("%d " % line_number)
        for ch in line:
            if quotes:
                buf.write(ch)
                if ch == '\"':
                    quotes = False
            elif ch == '\"':
                quotes = True
                buf.write(ch)
            else:
                if ch != ' ' and ch != '\t':
                    buf.write(ch)
        line_number += 1

s = buf.getvalue()

label_list = labels.keys()
label_list.sort(key=len, reverse=True)

for label in label_list:
    line_number = labels[label]
    s = s.replace("goto%s" % label, "goto%d" % line_number)
    s = s.replace("gosub%s" % label, "gosub%d" % line_number)
    s = s.replace("then%s" % label, "then%d" % line_number)
for name, value in consts.items():
    s = s.replace(name, value)


stdout.write(s)
