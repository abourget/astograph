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
import pdb


# POINTS OF FAILURE: when a multi-line comment comments out some include and context statements
# NOTE: the Goto things must be separated correctly with ? (and possibly ':'), and the goto destinations
#       must be correctly split with commas (,)
# TODO: add switch => support...

internal_contexts = ['parkedcalls']


contexts = []
links = []

# Match context opening things..
ctxmatch = re.compile(r'\[([^ ]+)\]')
# Match include calls..
incmatch = re.compile(r'^include ?=> ?([^ ]+)')
# Match Return() calls (consider this section as a macro)
retmatch = re.compile(r',Return\(\)')
# Peak at Gotos, make sure it's not in comments..
gotomatch = re.compile(r'(;?)[^;]+Goto(If(Time)?)?\((.+)\)\s*(;.*)?$', re.IGNORECASE | re.VERBOSE)

readfrom = sys.stdin
readfrom = open('extensions.conf')

def add_goto_context(curctx, newctx):
    """Just takes the ones with three arguments, and take the first.
    Add only if valid and not already linked within 'links'."""

    global contexts
    global links

    spl = newctx.split(',')

    if len(spl) == 3:
        # This is a context where we jump
        # TODO: add (curctx, spl[0], 'dotted')
        type1 = (curctx, spl[0])
        type2 = (curctx, spl[0], 'dotted')
        if type1 not in links and type2 not in links:
            links.append((curctx, spl[0], 'dotted'))

curctx = None
for l in readfrom.readlines():
    # TODO: work out the comments (especially the multi-line comments)
    ctx = ctxmatch.match(l)
    inc = incmatch.match(l)
    ret = retmatch.search(l)
    gto = gotomatch.search(l.strip())

    if ret:
        # Ok, we were in a Macro, make sure the context is not added.
        retctx = curctx

        if retctx in contexts:
            contexts.remove(retctx)
            
        # TODO: to be turbo safe, we should check the `links` to make
        # sure nothing was included from this macro context, but usually,
        # if you've created them with AEL2, you should never have an `include`
        # in the macro (or the sub)

        continue

    if ctx:
        if ctx.group(1) in ['general', 'globals']:
            curctx = None
            continue

        curctx = ctx.group(1)

        # Don't add macro- stuff.
        if curctx.startswith('macro-'):
            continue

        # Don't add it twice.
        if curctx not in contexts:
            contexts.append(curctx)

        continue

    if inc:
        if not curctx:
            raise Exception("include should not happen before a context definition")
        incctx = inc.group(1)

        # Add the internal contexts if we talk about them (like parkedcalls)OA
        if incctx in internal_contexts and incctx not in contexts:
            contexts.append(incctx)

        links.append((curctx, incctx, ''))

        continue

    if gto:
        # Skip commented out lines with Goto..
        if gto.group(1) == ';':
            continue

        # Let's parse TIME stuff..
        if gto.group(3):
            chkctx = gto.group(4).split('?')[-1]
            add_goto_context(curctx, chkctx)
        # Let's do GotoIf parsing..
        elif gto.group(2):
            chks = gto.group(4).split('?')[-1].split(':')
            add_goto_context(curctx, chks[0])

            # A second possible destination ?
            if len(chks) == 2:
                add_goto_context(curctx, chks[1])

        # Standard Goto parsing.. go ahead..
        else:
            chkctx = gto.group(4)
            add_goto_context(curctx, chkctx)
            
       
        ### Add links with style=dotted
        # make sure there's no ';' in front of the Goto
        # Check from the end the presence of a ? (got GotoIf), then parse the two possibilities, add two
        # Check the (curctx, gotoctx, '') doesn't exist in links (or as (curctx, gotoctx, 'style=dotted'))
        # then add it there..

        
dot = []
dot.append('digraph asterisk {\n')
#dot.append('  rankdir = LR;\n')

for x in contexts:
    dot.append('  "%s" [label="%s"];\n' % (x, x))

dot.append('\n')

for x in links:
    add = ''
    if len(x) == 3:
        add = ' [style="%s"]' % x[2]
    dot.append('  "%s" -> "%s"%s;\n' % (x[0], x[1].strip(), add))

dot.append('}\n')

f = open('graph.dot', 'w')
f.write(''.join(dot))
f.close()

sys.stdout.write(''.join(dot))
sys.stdout.flush()

# Gen the .dot thing, spit it to "dot -Tpng:cairo > output.png"
