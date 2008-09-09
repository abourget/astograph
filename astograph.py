#!/usr/bin/python
# -=- encoding: utf-8 -=-
# GPLv3 code
# Copyright: Alexandre Bourget (c) 2008
#
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
