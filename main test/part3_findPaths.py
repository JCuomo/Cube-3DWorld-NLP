#!/usr/bin/env python
# coding: utf-8


get_ipython().run_line_magic('reset', "-f")

import class_Astar_path as Astar_path
import class_dynamic_path as Astar_dynamic
import operator
import time
import random
import copy
import math
from copy import deepcopy
from scipy.spatial.distance import pdist
import numpy as np
import sys, os
from itertools import combinations_with_replacement
from itertools import combinations
from itertools import permutations
from itertools import product
from itertools import chain 
import fnmatch

# In[3]:


def deltasToCommands(deltas, block=None):
    commands = []
    #means that block info comes with deltas    
    if block==None:
        for t in deltas:
            block = t[0]
            direction = t[1]
            commands.append((("slide", block)+tuple(direction[:-1])))    
    else:
        if any(x[2]!=0 for x in deltas):
            commands.append(("grab", block))
            for direction in deltas:
                commands.append((("carry", block)+tuple(direction)))
            commands.append(("release", block))
        else:
            for direction in deltas:
                commands.append((("slide", block)+tuple(direction[:-1])))    
    return commands

def cmdToTuple(st_txt):
    st_t = (tuple(line[1:-1].split(" ")) for line in st_txt)
    return list(tuple(int(x) if x.isdigit() else x for x in t if x!="command") for t in st_t)

def stateToTuple(st_txt):
    st_t = (tuple(line[1:-1].split(" ")) for line in st_txt)
    return tuple(tuple(int(x) if x.isdigit() else x for x in t) for t in st_t)

def getCoordinates(st, block=None):
    # (has block1 location xpos ypos zpos)
    global list_of_blocks
    if block:    
        for t in st:
            if ("location" in t) and (block in t):
                return list(t[3:6])
        return []
    else:
        coords = dict()
        for b in list_of_blocks:
            coords[b] = getCoordinates(st, b)
        return coords

def getBlocks(st):
    blocks = []
    for t in st:
        for e in t:
            if type(e)!=int and "block" in e:
                blocks.append(e)
    return list(set(blocks))

def isEmptyCoordinate(obstacles,xyz):
    if xyz in obstacles:
        return False
    return True
        
def isValidCoordinate(xyz):
    x = xyz[0]
    y = xyz[1]
    try: 
        z = xyz[2] 
    except: 
        z = 0
        
    if 0 <= x < 10 and 0 <= y < 10 and 0 <= z:
        return True
    return False

def getClosestEmptyGrid_old(block):
    #TODO: needs improvement. It should be a search of the free grid closest from block and the block destination
    final = copy.copy(final_coordinates[block])
    next_grid = copy.copy(current_coordinates[block])
    i=0
    while(i<10):
        gradient = list(map(operator.sub, final, next_grid))
        delta = [max(min(x, 1), -1) for x in gradient]
        next_grid = list(map(operator.add, delta, next_grid))
        next_grid[2] = 0 # should be on the table
        if isValidCoordinate(next_grid) and isEmptyCoordinate(obstacles,next_grid):
            return next_grid
        i += 1
    while(1):
        next_grid = [random.randrange(0,10) for i in range(2)]+[0]
        if isValidCoordinate(next_grid) and isEmptyCoordinate(obstacles,next_grid):
            return next_grid

def getClosestEmptyGrid(block):
    global current_coordinates
    global final_coordinates
    global obstacles
    orig = current_coordinates[block][:2]
    orig = orig
    dest = final_coordinates[block][:2]
    dest = dest
    X = getDistanceMap(orig, dest, 2)
    while(1):
        m = divmod(X.argmin(), X.shape[1])
        m_ = [m[0],m[1],0]
        if isValidCoordinate(m_) and isEmptyCoordinate(obstacles,m_):
            return m_
        else:
            X[m] = np.inf
            
def getDistanceMap(orig, dest, k):
    orig = orig[:2]
    dest = dest[:2]
    i_coords, j_coords = np.meshgrid(range(10), range(10), indexing='ij')
    M = np.array([i_coords, j_coords])
    D = np.zeros(shape=(10,10))
    shortest_distance = getDistance(orig, dest)
    for i in range(10):
        for j in range(10):
            #S[i,j] = getDistance(M[:,i,j],b)
            D[i,j] = getDistance(M[:,i,j],dest) + k*getDistance(M[:,i,j],orig) - shortest_distance  
    return D

def getDistance( c1,c2):
    return pdist([c1,c2], 'chebyshev')[0]
    #return cdist([c1],[c2],'chebyshev')[0][0]

def getClosestCoord(xyz, coords_list): 
    '''returns the closest coord from "coords_list" to "xyz"'''
    closest = xyz #shouldn't never return this
    shortest_path = np.inf
    for c in coords_list:
        l = getDistance(c,xyz)
        if l < shortest_path:
            closest = c
            shortest_path = l
    return closest

def getClosestEmptyCoord(xyz, coords_list): 
    global obstacles
    c = list(np.append(getClosestCoord(xyz, coords_list), [0]))
    while not isEmptyCoordinate(obstacles,c): 
        coords_list.remove(c[:2])
        c = list(np.append(getClosestCoord(xyz, coords_list), [0]))
    return c

def getNeighbors(xyz, obstacles):
    blocking = []
    free = []
    for direction in list(product([-1,0,1], repeat=2)):
        direction = list(direction)+[0]
        if all(v == 0 for v in direction): continue
        neighbor = [sum(x) for x in zip(direction, xyz)]
        if isEmptyCoordinate(obstacles, neighbor) and isValidCoordinate(neighbor):
            free.append(neighbor)
        if not isEmptyCoordinate(obstacles, neighbor) and isValidCoordinate(neighbor):
            blocking.append(neighbor)
    return free, blocking

def findOrder():
    l = []
    for b in list_of_blocks:
        free, blocking = getNeighbors(final_coordinates[b], list(final_coordinates.values())) 
        l.append([b,len(free),len(blocking)])
    return [x[0] for x in sorted(l, key=operator.itemgetter(1, 2))]


# In[4]:


def genStackingCommands(solution):
    cmds = []
    global obstacles
    global current_coordinates
    for s in solution:
        b1 = s[1]
        b2 = s[2]
        origin = current_coordinates[b1]
        if b2 == "table":
            destination = getClosestEmptyGrid(b1)
        else:
            destination = copy.copy(current_coordinates[b2])
            destination[2] = destination[2]+1
            
            try: #maybe the is not a possible move to optimize
                final_dest = final_coordinates[b1]
                if getDistance(origin, destination) > getDistance(origin, final_dest)+1:
                    cmds_int = genIntermediatedSlidingCommands(s)
                    cmds += cmds_int
                    destination = copy.copy(current_coordinates[b2])
                    destination[2] = destination[2]+1
                    #print("block3",current_coordinates["block3"])
            except:
                pass
        deltas = searcher.AstarPathDelta(origin, destination, obstacles)
        cmds += deltasToCommands(deltas,b1)
        current_coordinates[b1] = destination
        obstacles = list(current_coordinates.values())
    return cmds

def genIntermediatedSlidingCommands(s):
    cmds = []

    global obstacles
    global current_coordinates
    global final_coordinates
    
    b1 = s[1]
    b2 = s[2]
    b1_c = current_coordinates[b1]
    origin = current_coordinates[b2]
    dest = final_coordinates[b2]
    #list of all grids on the optimal path
    coords_list = np.transpose(np.where(getDistanceMap(origin, dest, 1) == 0)).tolist()
    #find the closest empty grid in the path of b2 to its destination and b1, so when stacking b1 on b2
    #no extra steps are taken
    b2_interm_dest = getClosestEmptyCoord(b1_c[:2], coords_list)
    #find the path to that intermidiate position
    deltas = searcher.AstarPathDelta(origin, b2_interm_dest, obstacles)
    cmds += deltasToCommands(deltas,b2)
    current_coordinates[b2] = b2_interm_dest
    obstacles = list(current_coordinates.values())
    return cmds


def genSlidingCommands(dim=2):
    cmds = []
    global obstacles
    global current_coordinates
    global final_coordinates
    for b in findOrder():
        origin = current_coordinates[b]
        destination = final_coordinates[b]
        if origin == destination: continue
        if origin[2]!=0 or destination[2]!=0: continue #only slide blocks with height 0 to height 0
        if not isEmptyCoordinate(obstacles, destination):
            #move the annoying block 1 grid
            annoying_block = getBlockInCoord(destination)
            annoying_block_destination = getClosestEmptyGrid(annoying_block)
            annoying_block_origin = destination
            deltas = searcher.AstarPathDelta(annoying_block_origin, annoying_block_destination, obstacles, dim)
            cmds += deltasToCommands(deltas,annoying_block)
            current_coordinates[annoying_block] = annoying_block_destination
            obstacles = list(current_coordinates.values())
        deltas = searcher.AstarPathDelta(origin, destination, obstacles, 2)
        cmds += deltasToCommands(deltas,b)
        current_coordinates[b] = destination
        obstacles = list(current_coordinates.values())
            
    return cmds

def genSlidingCommandsLastChoice(dim=2):
    cmds = []
    global obstacles
    global current_coordinates
    global final_coordinates
        
    solution,_ = dynSearcher.AstarPath(deepcopy(current_coordinates), deepcopy(final_coordinates))
    cmds += deltasToCommands(dynSearcher.getDeltas(solution))
    for n in solution:
        if n.move==None: continue
        b = n.move[0]
        c = [n.move[1]]
        current_coordinates[b] = c
    obstacles = list(current_coordinates.values())
            
    return cmds


def genSlidingCommandsLastChoice2(dim=2):
    cmds = []
    global obstacles
    global current_coordinates
    global final_coordinates
    for b in findOrder():
        origin = current_coordinates[b]
        destination = final_coordinates[b]
        if origin == destination: continue
        if origin[2]!=0 or destination[2]!=0: continue #only slide blocks with height 0 to height 0
        solution_nodes,_ = searcher.AstarPath(origin, destination, None, dim)
        solution = searcher.getCoords(solution_nodes)
        # get the first annoying block in the path
        ab_coord = next(value for value in solution if value in obstacles)
        #if there is an obstacle in the solution path
        while ab_coord:
            moveAnnoyingBlock(ab_coord)
            try:
                ab_coord = next(value for value in solution if value in obstacles)
            except:
                break
        deltas = searcher.getDeltas(solution_nodes)
        cmds += deltasToCommands(deltas,b)
        current_coordinates[b] = destination
        obstacles = list(current_coordinates.values())
            
    return cmds


        
def cmdsToPaths(initial_coords, cmds):
    coords = copy.copy(initial_coords)
    paths = []
    for cmd in cmds:
        if 'grab' in cmd or 'release' in cmd: continue
        block = cmd[1]
        delta = cmd[2:]
        coord = coords[block]
        try:
            destination = [coord[0]+delta[0],coord[1]+delta[1],coord[2]+delta[2]]
        except:
            destination = [coord[0]+delta[0],coord[1]+delta[1],coord[2]]
        coords[block] = destination
        paths.append([block, destination])
    return paths


# In[5]:
def printCmdsToFile(cmds, filename):
    #[('grab', 'block2'), ('carry', 'block2', -1, -1, -1), ('carry', 'block2', 0, 0, -1), ('carry',.....
    with open(filename, 'w') as f:
        for t in cmds:
            l=len(t)
            j=0
            print("(", end='', file=f)
            for i in t:
                j+=1
                if j==l:
                    print(i, end='', file=f)
                else:
                    print(i, end=' ', file=f)
            print(")", file=f)


def getBlockInCoord(xyz):
    global current_coordinates
    for b,c in current_coordinates.items():
        if c==xyz:
            return b
    return ""


# In[6]:


global start_state
global goal_state
global current_coordinates
global list_of_blocks
global obstacles
global final_coordinates

test_n = ""

relations_filename = "tests/"+test_n+"relations"
start_filename = "tests/"+test_n+"start_defined"
goal_filename = "tests/"+test_n+"goal_defined"

try:    
    solutionFile = open(relations_filename,"r")
    solution_stack = cmdToTuple(list(x.rstrip() for x in solutionFile if "stack" in x))
    
    startFile = open(start_filename,"r")
    start_state = cmdToTuple(list(x.rstrip() for x in startFile))
    
    goalFile = open(goal_filename,"r")
    goal_state = cmdToTuple(list(x.rstrip() for x in goalFile))
except:
    print("error loading files:", relations_filename,start_filename,goal_filename )

list_of_blocks = getBlocks(start_state)
start_coordinates = getCoordinates(start_state)
current_coordinates = getCoordinates(start_state)
obstacles = getCoordinates(start_state).values()
final_coordinates = getCoordinates(goal_state)
searcher = Astar_path.Astar_path()
dynSearcher = Astar_dynamic.Astar_dynamic_path()

cmds1 = genStackingCommands(solution_stack)
try:
    cmds2 = genSlidingCommands()
except:
    print("Trying with dynamic reordering")
    cmds2 = genSlidingCommandsLastChoice()

paths_filename = "tests/"+test_n+"paths"

print("Steps:",len(cmds1+cmds2))
printCmdsToFile(cmds1+cmds2, paths_filename)




