#!/usr/bin/env python
# coding: utf-8


import sys, os

start_f = sys.argv[1]
goal_f = sys.argv[2]

try:
    if not os.path.exists("tests"):
        os.makedirs("tests")
except OSError:
    print ('Error: Creating "tests" folder..do it manually')

get_ipython().run_line_magic('run', "-i 'parser.py' 'move red block on top of blue block.' 'goal.txt'")
print("Goal parsed")

get_ipython().run_line_magic('run', "-i 'part1_findGoal_v2.py'  $start_f 'goal.txt'")
print("Goal defined")

get_ipython().run_line_magic('run', "-i 'part2_findStackMoves.py'")
print("Stacking relations solved")

get_ipython().run_line_magic('run', "-i 'part3_findPaths.py'")

