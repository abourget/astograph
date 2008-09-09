#!/usr/bin/python
# -=- encoding: utf-8 -=-
#
# Copyright (C) 2008 - Alexandre Bourget
#
# Author: Alexandre Bourget <alex@bourget.cc>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import sys

# POINTS OF FAILURE: when a multi-line comment comments out some include and context statements

contexts = []
links = []

ctxmatch = re.compile(r'\[([^ ]+)\]')
incmatch = re.compile(r'^include ?=> ?([^ ]+)')

curctx = None
for l in sys.stdin.readlines():
    # TODO: work out the comments (especially the multi-line comments)
    ctx = ctxmatch.match(l)
    inc = incmatch.match(l)

    if ctx:
        if ctx.group(1) in ['general', 'globals']:
            curctx = None
            continue

        curctx = ctx.group(1)
        contexts.append(curctx)
    if inc:
        if not curctx:
            raise Exception("include should not happen before a context definition")
        links.append((curctx, inc.group(1)))
        
dot = []
dot.append('digraph asterisk {\n')
for x in contexts:
    dot.append('  "%s" [label="%s"];\n' % (x, x))

dot.append('\n')

for x in links:
    dot.append('  "%s" -> "%s";\n' % (x[0], x[1].strip()))

dot.append('}\n')

f = open('graph.dot', 'w')
f.write(''.join(dot))
f.close()

sys.stdout.write(''.join(dot))
sys.stdout.flush()

# Gen the .dot thing, spit it to "dot -Tpng:cairo > output.png"
