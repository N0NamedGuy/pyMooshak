#!/usr/bin/env python2
#
# (C) 2011 David Miguel de Araújo Serrano
#
# This file is part of pyMooshak.
# 
# pyMooshak is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pyMooshak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyMooshak.  If not, see <http://www.gnu.org/licenses/>.

from Mooshak import Mooshak
import json
import sys

MOOSHAK_JSON='mooshak.json'

def getcfg():
    f = open(MOOSHAK_JSON)
    cfg = json.load(f)
    f.close()

    return cfg

def strsub(sub):
    return "%s\t%s\t%s\t%s\t\t%s\t%s\t%s" % (
        sub['number'], sub['time'], sub['team'], sub['problem'], sub['language'],
        sub['result'], sub['state'])



cmd = ""
args = []
if len(sys.argv) > 1:
    cmd = sys.argv[1]

    if len(sys.argv) > 2:
        args = sys.argv[2:]

cfg = getcfg() 
moo = Mooshak(cfg['baseurl'])

# pymooshak submit <file> 
if cmd == 'submit':
    result = moo.submit(cfg['contest'], cfg['user'], cfg['password'], str(cfg['problem']),
        str(" ".join(args)))

    last_sub = moo.get_last_result(cfg['contest'], cfg['user'])
    if last_sub == None:
        print 'Way too many submissions are being done... Won\'t tell your result.'
    else:
        print result
        print strsub(last_sub)

# pymooshak problems <contest>
elif cmd == 'problems':
    probs = moo.list_problems(cfg['contest'])
    print "Problems in %s:" % (cfg['contest']) 
    for p in probs:
        print p + ": " + probs[p]

# pymooshak contests
elif cmd == 'contests':
    contests = moo.list_contests()
    for c in contests:
        print c + ": " + contests[c]

else:
    print "PyMooshak by David Serrano"
    print "Usage:"
    print "\tpymooshak submit <file>"
    print "\tpymooshak contests"
    print "\tpymooshak problems <contest>"


