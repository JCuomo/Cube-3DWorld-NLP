#!/usr/bin/env python
# coding: utf-8

# In[1]:


from copy import deepcopy 
import sys, os
from itertools import combinations_with_replacement
from itertools import combinations
from itertools import permutations
from itertools import product
from itertools import chain 
import time
import math
import numpy as np
import fnmatch
from itertools import chain 
import operator
from scipy.spatial.distance import pdist


# In[2]:


from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"


# <a id='OTHERS'></a>
# ### OTHERS

# In[3]:


def stateToTuple(st_txt):
    st_t = (tuple(line[1:-1].split(" ")) for line in st_txt)
    return tuple(tuple(int(x) if x.isdigit() else x for x in t) for t in st_t)


# In[4]:


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


# In[5]:


def nCr(n,r):
    f = math.factorial
    return f(n+r-1) / f(r) / f(n-1)


# In[6]:


def printCommand(command):
    if command:
        print("("+command[0]+" "+command[1]+" "+command[2]+")")

def printState(state):
    for t in state:
        #final version: print("("+t[0]+" "+t[1]+" "+t[2]+" "+t[3]+")")
        print(t)
        #print(t[1]+" "+t[3]+" "+t[2])

def printStateToFile(state, filename):
    with open(filename, 'w') as f:
        for t in state:
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


# In[7]:


def isGoal(goal_state, state):
    return all(conditionsMet(goal_state,state))


# In[8]:


def removeDuplicates(states):
    x_copy = states[:]
    removed = 0
    for i, s in enumerate(states):
        if any(isGoal(s,b) for b in x_copy[:i-removed]):
            del x_copy[i-removed]
            removed += 1
    return x_copy


# In[9]:


def getCombinations(coords):
    perm = list(product(*coords))
    if perm:
        return perm
    else:
        c = [x for x in coords if x]
        if len(c)==1:
            return c
    return []

def intersection(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3 

def getSideGrids(xyz):
    xy = xyz[:2]
    side_grids = []
    for direction in [[0,1], [1,0], [0,-1], [-1,0]]:
        c = tuple([sum(x) for x in zip(xy, direction)]+[xyz[2]])
        if isValidCoordinate(c):
            side_grids.append(c)
    return side_grids


# <a id='GET'></a>
# ### GET METHODS

# In[10]:


def getBlocks(st):
    blocks = []
    for t in st:
        for e in t:
            if type(e)!=int and "block" in e:
                blocks.append(e)
    return list(set(blocks))

def getHeight(st, block):
    b = onTopOf(st, block)
    if b in [None, "table"]:
        return 0
    else:
        return 1 + getHeight(st, b)

def getDepth(st, block):
    b = underneathOf(st, block)
    if b in [None]:
        return 0
    else:
        return 1 + getDepth(st, b)
    
def getDistance(c1,c2):
    return pdist([c1,c2], 'chebyshev')[0]
    #return math.sqrt(sum([(a - b) ** 2 for a, b in zip(c1, c2)]))    
    


# In[11]:


def getCoordinates(st, block=None):
    # (has block1 location xpos ypos zpos)
    global list_of_blocks
    
    if block:    
        coords = []
        for t in st:
            if ("location" in t) and (block in t):
                coords.append(t[3:6])
        return coords
    else:
        coords = dict()
        for b in list_of_blocks:
            coords[b] = getCoordinates(st, b)
        return coords
    
def getColors(st, block=None):
    # (has block1 location xpos ypos zpos)
    global list_of_blocks
    if block:    
        for t in st:
            if ("color" in t) and (block in t):
                return t[3]
        return "undefined"
    else:
        colors = dict()
        for b in list_of_blocks:
            colors[b] = getColors(st, b)
        return colors


# <a id='COORDINATES'></a>
# ### COORDINATES

# In[12]:


def getCoordinateRestrictions(st):
    '''Returns a dictionary of blocks with all possible locations for each'''
    coords =  getCoordinates(st)
    for t in st:
        b1 = t[1]
        b2 = t[2]
        if "wildcard" in b1 or "wildcard" in b2: continue
        if "side-by-side" in t:
            c1 = coords[b1]
            c2 = coords[b2]
            if len(c1)==1:
                c1=c1[0]
                if c2==[]:
                    possible_c2 = [(c1[0]+1,c1[1],c1[2]),(c1[0]-1,c1[1],c1[2]),(c1[0],c1[1]+1,c1[2]),(c1[0],c1[1]-1,c1[2])]
                    coords[b2] = list(x for x in possible_c2 if (isValidCoordinate(x) and isEmptyCoordinate(x,st)))
                elif len(c2)>1: # new possible locations => intersect new with old
                    possible_c2 = [(c1[0]+1,c1[1],c1[2]),(c1[0]-1,c1[1],c1[2]),(c1[0],c1[1]+1,c1[2]),(c1[0],c1[1]-1,c1[2])]
                    new_c = list(x for x in possible_c2 if (isValidCoordinate(x) and isEmptyCoordinate(x,st)))
                    coords[b2] = list(set(new_c).intersection(c2))
            elif len(c2)==1:
                c2=c2[0]
                if c1==[]:
                    possible_c1 = [(c2[0]+1,c2[1],c2[2]),(c2[0]-1,c2[1],c2[2]),(c2[0],c2[1]+1,c2[2]),(c2[0],c2[1]-1,c2[2])]
                    coords[b1] = list(x for x in possible_c1 if (isValidCoordinate(x) and isEmptyCoordinate(x,st)))
                elif len(c1)>1: # new possible locations => intersect new with old
                    possible_c1 = [(c2[0]+1,c2[1],c2[2]),(c2[0]-1,c2[1],c2[2]),(c2[0],c2[1]+1,c2[2]),(c2[0],c2[1]-1,c2[2])]
                    new_c = list(x for x in possible_c1 if (isValidCoordinate(x) and isEmptyCoordinate(x,st)))
                    coords[b1] = list(set(new_c).intersection(c1))
    return coords


# In[13]:


def isSameXYGrid(c1,c2):
    return c1[0]==c2[0] and c1[1]==c2[1]

def isAdjacentGridXY(c1,c2):
    return ((c1[0]==c2[0] and (c1[1]==c2[1]+1 or c1[1]==c2[1]-1))
            or (c1[1]==c2[1] and (c1[0]==c2[0]+1 or c1[0]==c2[0]-1))) and c1[2]==c2[2]

def isAdjacentGridZ(c1,c2):
    return c1[0]==c2[0] and c1[1]==c2[1] and (c1[2]==c2[2]+1 or c1[2]==c2[2]-1)

def mayBeOnTop(top,bot):
    return top[0]==bot[0] and top[1]==bot[1] and top[2]==bot[2]+1 or top==[] or bot==[] and bot[2]>=0 and top[2]>0

def canBeHeight0(st,b):
    cs = getCoordinates(st,b)
    for c in cs:
        if c[2]>0:
            return False
    return True

def isHeight0(st,b):
    cs = getCoordinates(st,b)
    for c in cs:
        if c[2]==0:
            return True
    return False

def isEmptyCoordinate(xyz, st=None):
    global global_coords
    
    if st:
        for t in st:
            if ("location" in t) :
                if  (xyz == t[3:6]):
                    return False
    else:
        if xyz in chain(*global_coords.values()): 
            return False
    return True
        
def isValidCoordinate(xyz):
    x = xyz[0]
    y = xyz[1]
    z = xyz[2]
    if 0 <= x < 10 and 0 <= y < 10 and 0 <= z:
        return True
    return False

def getClosestEmptyCoord(xyz, h=None, forbidden=None): 
    for c in getOrderedCoords(xyz,h):
        c = tuple(c)
        if isEmptyCoordinate(c) and c not in forbidden: 
            return c

def getOrderedCoords(xyz, h=None):
    l = []
    repeat=3
    if h: repeat=2
    for g in product(range(10),repeat=repeat):
        if h: g = tuple((g[0],g[1],h))
        l.append((g,getDistance(g,xyz)))
    return [list(x[0]) for x in sorted(l, key=operator.itemgetter(1))]


# In[14]:


def getFinalCoordinates(st, start_state):
    '''It should be called once at the end and will assign the locations closer to the start point for
    those blocks that have many possibilities'''
    global global_coords
    global list_of_blocks
    debug = 0
    if not isValidState(st):
        sys.exit("Run again please")
    
    getFinalCoords_aux(st, start_state)
    
    #fb:floating block, psbs:possible support blocks
    floatingB, psbs = getBlocksFloating(st)
    while(floatingB!=None):
        floatingB_c = global_coords[floatingB]
        psb_c = list(deepcopy(global_coords[floatingB][0]))
        psb_c[2] =  psb_c[2]-1
        psb = getClosestUndefinedBlock(psb_c, psbs)
        psb_c = tuple(psb_c)
        global_coords[psb] = [psb_c]
        st += ((("has", psb, "location")+psb_c),)
        if debug: 
            print("condC",(("has", psb, "location")+psb_c))
        st = getRelationsAndLocations(st)   
        getFinalCoords_aux(st, start_state)
        floatingB, psbs = getBlocksFloating(st)

    expanded_coords = {}
    for b in list_of_blocks: expanded_coords[b] = [(99,99,99)]
    aux_global_coords = deepcopy(global_coords)

    j = 0
    while 1:
        j += 1
        aux_st = deepcopy(st)
        global_coords = deepcopy(aux_global_coords)
        informedLookDict = getCoordinateRestrictions(st)
        for bx, cx in global_coords.items():
            if len(cx) == 0:
                try:
                    orig_c = next(x for x in informedLookDict[bx] if x not in expanded_coords[bx])
                except:
                    h = getHeight(aux_st, bx)
                    if h==0 and onTopOf(aux_st, bx)==None:
                        h = None
                    orig_c = getClosestEmptyCoord(getCoordinates(start_state, bx)[0],h, forbidden=expanded_coords[bx])                    
                aux_st += ((("has", bx, "location")+orig_c),)
                global_coords[bx] = [orig_c]
                if debug: print("condD",("has", bx, "location")+orig_c)
                aux_st = getRelationsAndLocations(aux_st) 
                getFinalCoords_aux(aux_st, start_state)
        floatingB, psbs = getBlocksFloating(aux_st)
        if isValidState(aux_st) and floatingB==None:
            st = aux_st
            return global_coords
        else:
            for b in list_of_blocks:
                if aux_global_coords[b] != global_coords[b] and global_coords[b][0][2]!=0:
                    expanded_coords[b] = expanded_coords[b] + global_coords[b]


# In[15]:


def getFinalCoords_aux(st, start_state):
    global global_coords
    global list_of_blocks
    debug = 0
    copy_global_coords = dict()
    while(copy_global_coords != global_coords):
        copy_global_coords = deepcopy(global_coords)
        for b,c in global_coords.items():
            n_possibilities = len(c)
            if n_possibilities == 1:
                st += ((("has", b, "location")+c[0]),)
                st = getRelationsAndLocations(st)
                if debug: print("condA",("has", b, "location")+c[0])
            elif n_possibilities > 1:
                c_start = getCoordinates(start_state, b)[0]
                chose_c = [c[np.argmin(list(getDistance(c_start,x) for x in c))]]
                global_coords[b] = chose_c
                st += ((("has", b, "location")+chose_c[0]),)
                if debug: print("condB",("has", b, "location")+chose_c[0])
                st = getRelationsAndLocations(st)
    return st


# In[16]:


def getClosestUndefinedBlock(xyz, blocks):
    global start_state
    closest = blocks[0]
    s = np.inf
    for b in blocks:
        c = getCoordinates(start_state, b)[0]
        dist = getDistance(xyz,c)
        if dist < s:
            s = dist
            closest = b
    return closest


# In[17]:


def getBlocksFloating(st):
    global global_coords
    for b1,c1 in global_coords.items():
        if len(c1)!=1 : continue
        c1=c1[0]
        if c1[2]==0: continue #has to be defined and not be on the table
        h1 = c1[2]
        c = (c1[0],c1[1],h1-1)
        if any((len(c0)==1 and c==c0[0]) for c0 in global_coords.values()): continue
        #if c in chain(*global_coords.values()): continue #if the coordinate is occupied, it's not floating
        possibles = []
        for b0,c0 in global_coords.items():
            if b0==b1: continue
            l = len(c0)
            if l==0:
                possibles.append(b0)
            else:
                for c0_c in c0:
                    if c==c0_c[0]: 
                        possibles.append(b0)
                        break
        return (b1,possibles)
    return (None, [None])


# <a id='RELATIONS'></a>
# ### RELATIONS

# In[18]:


def onTopOf(st, block):
    l = []
    for t in st:
        if ("on-top-of" in t) and (t[1] == block):
            l.append(t[2])
    if len(l)==1:
        return l[0]
    elif len(l)>1:
        return l
    else:
        return None

def underneathOf(st, block):
    l = []
    for t in st:
        if ("on-top-of" in t) and (t[2] == block):
            l.append(t[1])
    if len(l)==1:
        return l[0]
    elif len(l)>1:
        return l
    else:
        return None

def sideBySide(st, block):
    side_blocks = []
    for t in st:
        if ("side-by-side" in t) and (block in t):
            if block==t[1]:
                side_blocks.append(t[2]) 
            else:
                side_blocks.append(t[1]) 
    side_blocks = list(set(side_blocks))
    #try:
    #    side_blocks.remove(block)
    #except:
    #    None
    return side_blocks


# In[19]:


def isClusterOnTable(st,cluster):
    for c in cluster:
        if onTopOf(st,c) not in [None,"table"]:
            return False
    return True

def combineListWithCommonElements(list_of_list):
    # merge list_of_list with common blocks
    out = []
    while len(list_of_list)>0:
        first, *rest = list_of_list
        first = set(first)

        lf = -1
        while len(first)>lf:
            lf = len(first)
            rest2 = []
            for r in rest:
                if len(first.intersection(set(r)))>0:
                    first |= set(r)
                else:
                    rest2.append(r)     
            rest = rest2

        out.append(first)
        list_of_list = rest
    return out

def overlapRelations(st, relation):
    ''' Given the relation -, then if (a-b) and (b-c) the output will be (a,b,c)'''
    pairs=[] 
    for t in st:
        if relation in t:
            if(t[1] == "table" or t[2] == "table"): continue 
            pairs.append([t[1], t[2]])
    return combineListWithCommonElements(pairs)


# In[20]:


def getClusters(st):
    '''returns clusters of block that share at least one block on its side'''
    return overlapRelations(st, "side-by-side")



def getSameLevelBlocks(st):
    '''returns clusters of block that share at least one block on its side'''
    coords = getCoordinates(st)
    onTable = []
    levels = {}
    for b,c in coords.items():
        if c:
            lvl = c[0][2]
            levels[lvl] = levels[lvl]+[b] if lvl in levels else [b]
            if lvl==0:
                onTable.append(b)
    for s in st:
        if "table" in s:
            onTable.append(s[1])
    set_onTable = set(onTable)
    list_of_list = []
    for i in levels.values(): # byLocations
        if len(set(i).intersection(set_onTable)) > 0: #means at least one block is no table
            list_of_list.append(i+onTable)
        else:
            list_of_list.append(i)        
    for i in getClusters(st): # byRelations
        if len(i.intersection(set_onTable))>0: #means at least one block is no table
            list_of_list.append(list(i)+onTable)
        else:
            list_of_list.append(list(i))

    return combineListWithCommonElements(list_of_list)

def getDifferentLevelBlocks(st):
    '''returns towers'''
    
    coords = getCoordinates(st)    
    
    levels = {}
    byLocation = []
    for b,c in coords.items():
        if c: levels[b] = c[0][2]
            
    for b1,c1 in coords.items():
        l = []
        blocks = []
        if c1:
            blocks.append(b1)
            l.append(levels[b1])
            for b2,c2 in coords.items():
                if b1==b2 or not c2: continue
                if levels[b2] not in l:
                    blocks.append(b2)
                    l.append(levels[b2])
            byLocation.append(blocks)

    #byLocation = [list(x) for x in set([ tuple(set(i)) for i in byLocation ])]
    byRelations = []
    for i in overlapRelations(st, "on-top-of"): # byRelations
        byRelations.append(list(i))
    return  [set(x) for x in set([ frozenset(i) for i in  byRelations + byLocation  ])]


# In[ ]:





# In[ ]:





# In[21]:


def getRelationsFromRelations(st, implicit=None, prev_w=None):
    #notation: b=block, letter=pos(X,Y), number=pos(Z). E.g.: bA1=block in grid A and height 1      
    #notation: sbs = side by side, ot = on top
    #if implicit==[]:
    #    return None, False
    global list_of_blocks
    global D
    debug = D
    implicit_state_tuples = []
    reRun_flag = False
    invalid_flag = False
    if prev_w==None:
        prev_w = [] # warnings list
    w = []    
    if debug: print("New Run")
    #STAGE 1 of inference
    for bA1 in list_of_blocks: # for the search of implicit conditions I assume the block i'm checking for is on top
        bA0 = onTopOf(st, bA1)
        if bA0 != None and bA0 != "table":  # if bA1 is on top of a block (bA0)
            for bx0 in sideBySide(st, bA0): # for each block sbs to bA0
                bx1 = underneathOf(st, bx0)
                if bx1 != None and type(bx1)==str: # if bx0 has a block on top
                    # bA1 bx1 ==> if bx1 exists then bA1<-sbs->bx1
                    # bA0 bx0 ==> bA1->bA0->bx0->bx1----close the loop--->bA1
                    implicit_state_tuples.append(("is",bx1,bA1,"side-by-side"))
                    if debug: print("condition 1: is",bx1,bA1,"side-by-side")
            for bx1 in sideBySide(st, bA1):
                bx0 = onTopOf(st, bx1)
                if bx0 != None and type(bx0)==str: # if bx1 is on top of a block (bx0)
                    # "(is block4 block5 on-top-of)",
                    # "(is block7 block6 on-top-of)",
                    # "(is block7 block4 side-by-side)",
                    # IMPLY: "(is block6 block5 side-by-side)"
                    # bA1 bx1 ==> if bx0 exists then bA0<-sbs->bx0
                    # bA0 bx0 ==> bA0->bA1->bx1->bx0----close the loop--->bA0
                    implicit_state_tuples.append(("is",bx0,bA0,"side-by-side"))
                    
                    if debug: 
                        print("bA0",bA0,"->bA1",bA1,"->bx1",bx1,"->bx0",bx0)
                        print("condition 2: is",bx0,bA0,"side-by-side")
        elif bA0 == None: # if bA1 is not on top of a block (explicitly)
            for bx1 in sideBySide(st, bA1): # for each block sbs to bA1
                bx0 = onTopOf(st, bx1)
                if bx0 != None and bx0 != "table": # if bx1 is on top of a block (bx0)
                    possible_underneath_blocks = []
                    for by0 in sideBySide(st, bx0):
                        if not underneathOf(st, by0):
                            possible_underneath_blocks.append(by0)
                    if len(possible_underneath_blocks) > 1:
                        w.append((bA1,"ambiguous"))
                        # print("Warning: "+bA1+" can be on top of more than one block")
                    elif len(possible_underneath_blocks) == 0:
                        w.append((bA1,"nothing"))
                        # print("Warning: "+bA1+" has no block to be on top of")
                    else:
                        implicit_state_tuples.append(("is",bA1,possible_underneath_blocks[0],"on-top-of"))
                        if debug: print("condition 3: is",bA1,possible_underneath_blocks[0],"on-top-of")
        # complete the side by side relations
        for sbs_block in sideBySide(st, bA1):
            implicit_state_tuples.append(("is",bA1,sbs_block,"side-by-side"))
            implicit_state_tuples.append(("is",sbs_block,bA1,"side-by-side"))
            if debug: print("condition 4: is",sbs_block,bA1,"side-by-side")
            
    #STAGE 2 of inference
    aux_state = st+tuple(implicit_state_tuples) #TODO: simplificar para que no haya repeticiones
    extra_implicit_state_tuples = []
    for b1 in list_of_blocks:
        b0 = onTopOf(aux_state, b1)
        h = []
        if b0 == None:      
            
            for sbs in sideBySide(aux_state,b1):
                h.append(getHeight(aux_state, sbs))
            # if all sbs blocks have height 0 or it doesn't have sbs blocks:
            if ((h and all(i==0 for i in h)) or h==[]) and isHeight0(aux_state,b1): #canBeHeight0(aux_state,b1):
                 # assign blocks to be on top of the table if they aren't on top of any other block and their side blocks have Height=0
                extra_implicit_state_tuples.append(("is",b1,"table","on-top-of"))   
                if debug: print("condition 5: is",b1,"table","on-top-of")
            elif implicit == []: # if reRun didn't return anything new, make stronger inference
                found_valid_state = False
                # if all sbs blocks have equal height or it doesn't have sbs blocks:
                if (h and h[1:] == h[:-1]):
                    D=0
                    for b2 in list_of_blocks:
                        possible_new_condition = ("is",b1,b2,"on-top-of")  
                        #if isValidState(tuple(extra_implicit_state_tuples)+aux_state+(possible_new_condition,)):
                        if isValidState(aux_state+(possible_new_condition,)):
                            if found_valid_state: #if there are more than 1 valid state => is ambiguous
                                w.append((b1,"ambiguous"))
                                if debug: print("ambiguous")
                                reRun_flag = False
                                found_valid_state = False
                                break
                            else: #if there is only 1 valid state, re run to check new implicit conditions
                                #extra_implicit_state_tuples.append(new_condition)                 
                                reRun_flag = True
                                if debug: print("re run on by 1")
                                found_valid_state = True
                                new_condition = possible_new_condition
                    D=1
                    if found_valid_state:
                        extra_implicit_state_tuples.append(new_condition)
                        if debug: print("condition 6:",new_condition)
            else: #if the sbs have Height>0 recheck for implicit conditions
                reRun_flag = True
                if debug: print("re run on by 2")

    # remove repetitions and merge both stages of inference
    implicit_state_tuples = list(set(implicit_state_tuples+extra_implicit_state_tuples)-set(st)) 
    #STAGE 3 of inference (recursive)
    extra_implicit_state_tuples = None
    if reRun_flag: #recheck for implicit conditions
        extra_implicit_state_tuples,w = getRelationsFromRelations(st+tuple(implicit_state_tuples),implicit_state_tuples)

    if extra_implicit_state_tuples == None:
        extra_implicit_state_tuples = ()
        
    #if implicit_state_tuples == [] or extra_implicit_state_tuples==():
    if (implicit_state_tuples == [] and reRun_flag==False):
        for warning in w:
            #print("Warning: "+warning[0]+" on top of "+warning[1])
            invalid_flag = True
            
    return tuple(implicit_state_tuples)+extra_implicit_state_tuples, w


# <a id='MIX'></a>
# ### MIX COORDINATES AND RELATIONS

# In[22]:


def getLocationsFromRelations(st):
    global global_coords
    global D
    debug = D
    #remove from all other blocks those coordinates that are defined
    for bx,cx in global_coords.items():
        if len(cx)==1:
            for by,cy in global_coords.items():
                if bx==by: continue
                if cx[0] in cy:
                    cy.remove(cx[0])
    new_st = st
    for b,xyz in global_coords.items():
        
        if len(xyz)!=1: # not defined coordinate
            # if it is on top of some block
            b0 = onTopOf(st,b)
            if b0 not in [None,"table"]: 
                xyz1 = global_coords[b0]
                if len(xyz1)==1: # and the block has defined coordinate
                    xyz1 = xyz1[0] # grab that well defined coordinate
                    global_coords[b] = [(xyz1[0],xyz1[1],xyz1[2]+1)]
                    new_st += ((("has", b, "location")+global_coords[b][0]),)
                    if debug: 
                        print("ST:", new_st)
                        print("consistent coord?",(xyz1[0],xyz1[1],xyz1[2]+1) in xyz, xyz)
                        print("cond1", ("has", b, "location")+global_coords[b][0])
                    continue
                else: # none of the two blocks has defined coordinates
                    possibles_coords = set((c[0],c[1],c[2]+1) for c in xyz1).intersection(set(xyz))
                    # TODO: I think I can add all coordinates from intersections
                    if len(possibles_coords)==1:
                        xyz1 = possibles_coords.pop()
                        global_coords[b] = [xyz1]
                        global_coords[b0] = [(xyz1[0],xyz1[1],xyz1[2]-1)]
                        if debug: 
                            print("cond2a", b, global_coords[b])
                            print("cond2b", b0, global_coords[b0])
                        continue
                    
                
            # if it is underneath of some block with defined coordinates
            b1 = underneathOf(st,b)
            if b1 not in [None,"table"]: 
                xyz1 = global_coords[b1]
                if len(xyz1)==1: # defined coordinate
                    xyz1 = xyz1[0] # grab that well defined coordinate
                    global_coords[b] = [(xyz1[0],xyz1[1],xyz1[2]-1)]
                    new_st += ((("has", b, "location")+global_coords[b][0]),)
                    if debug: print("cond3",("has", b, "location")+global_coords[b][0])
                    continue
            
            #if it has blocks next to it
            b_sbs = sideBySide(st,b)
            c_sbs = [global_coords[x] for x in b_sbs]
###################################################################################################################                   
            b_possibilities = []
            b_possibilities_for_all = []
            b_possibilities_for_each = []
            for cs in c_sbs: #for each block next to b
                b_possibilities_for_each = []
                for c in cs: #for each possible coordinate of that block
                    b_possibilities_for_each += getSideGrids(c)
                b_possibilities_for_all.append(list(set(b_possibilities_for_each)))
            
            for pair in list(combinations(b_sbs,2)):
                pair_coords = [global_coords[pair[0]], global_coords[pair[1]]]
                if pair_coords[0] and pair_coords[1]:
                    if pair_coords[1:] == pair_coords[:-1]:
                        pair_coords = pair_coords[0]
                        b1 = pair[0]
                        b2 = pair[1]
                        c1 = pair_coords[0]
                        c2 = pair_coords[1]
                        b_possibilities_for_all.append(intersection(getSideGrids(c1),getSideGrids(c2)))
                        #remove from all other blocks cause it should be used by one of these two
                        for bx,cx in global_coords.items():
                            if bx==b1 or bx==b2: continue
                            if c1 in cx:
                                cx.remove(c1)
                            if c2 in cx:
                                cx.remove(c2)
                    
            l = len(b_possibilities_for_all)
            for i in range(l):
                if b_possibilities_for_all[i]==[]: continue
                if b_possibilities==[]:
                    b_possibilities = b_possibilities_for_all[i]
                else:
                    b_possibilities = intersection(b_possibilities,b_possibilities_for_all[i])
                    
           # for pcs in getCombinations(c_sbs): #tries each possible combination of coordinates
           #     for pc in pcs: #for each coordinate get the possible side grids
           #         b_possibilities_for_each = getSideGrids(pc)
           #         print("b_possibilities: ", b_possibilities)
           #         print("b_possibilities_for_each: ", b_possibilities_for_each)
           #         if b_possibilities and b_possibilities_for_each:
           #             b_possibilities = intersection(b_possibilities,b_possibilities_for_each)
           #             #if the intersection is empty, it means this is not a possible combination
           #             if not b_possibilities: continue
           #         else: #first time
           #             b_possibilities = b_possibilities_for_each
           # # intersect all new possibilities with all previous ones
            if xyz:
                new_xyz = intersection(b_possibilities, xyz)
            else:
                new_xyz = b_possibilities
            global_coords[b] = new_xyz
            if len(new_xyz)==1:
                new_st += ((("has", b, "location")+new_xyz[0]),)
                if debug: print("cond4",("has", b, "location")+new_xyz[0])
###################################################################################################################  
                       
        #    if len(b_sbs) > 1: #it has to have at least two block by its side
        #        try: #a block might not have any assigned coordinates
        #            c_sbs = [coords[x][0] for x in b_sbs]
        #        except:
        #            continue
        #        # retrieve those coordinates that share an axis
        #        xyz12_aux = [i for i in c_sbs if any([i[0]==j[0] or i[1]==j[1] for j in [e for e in c_sbs if e!=i]])]
        #        xyz1 = xyz12_aux[0]
        #        xyz2 = xyz12_aux[1]
        #        #xyz1 = coords[b_sbs[xyz12_aux[0]]]
        #        #xyz2 = coords[b_sbs[xyz12_aux[1]]]
        #        # if they have defined coordinates and they share one axis => b is in the middle
        #        if len(xyz1)==1 and len(xyz2)==1: # defined coordinates:
        #            xyz1 = xyz1[0] # grab that well defined coordinate
        #            xyz2 = xyz2[0] # grab that well defined coordinate
        #            if xyz1[0]==xyz2[0]: # aligned in the x axis
        #                coords[b] = (xyz1[0],(xyz1[1]+xyz2[1])/2,xyz1[2])
        #                new_st += ((("has", b, "location")+coords[b]),)
        #            elif xyz1[1]==xyz2[1]: # aligned in the y axis
        #                coords[b] = ((xyz1[0]+xyz2[0])/2,xyz1[1],xyz1[2])
        #                new_st += ((("has", b, "location")+coords[b]),)
        else:
            new_st += ((("has", b, "location")+xyz[0]),)
            if debug: print("cond5", ("has", b, "location")+xyz[0])
    
    #remove from all other blocks those coordinates that are defined
    for bx,cx in global_coords.items():
        if len(cx)==1:
            for by,cy in global_coords.items():
                if bx==by: continue
                if cx[0] in cy:
                    cy.remove(cx[0])
    return tuple(set(new_st))

def getRelationsFromLocations(st):
    global global_coords
    new_st = st
    global D
    debug = D
    
    for b1,c1 in global_coords.items():
        if len(c1)!=1: continue
        c1 = c1[0]
        if c1[2] == 0: #the block is on the table
            new_st += (("is", b1, "table", "on-top-of"),) # b1 on top of table
            if debug: print("gRFL cond0:",("is", b1, "table", "on-top-of"))

        for b2,c2 in global_coords.items():   
            if b1==b2 or len(c2)!=1: continue 
            c2 = c2[0] #after checking that the coordinates are well-defined == one element in the list
            if c1[0]==c2[0] and c1[1]==c2[1]: #if they are in the same x,y grid
                if c1[2]==c2[2]+1:
                    new_st += (("is", b1, b2, "on-top-of"),) # b1 on top of b2
                    if debug: print("gRFL cond1:",("is", b1, b2, "on-top-of"))
                elif c1[2]==c2[2]-1:
                    new_st += (("is", b2, b1, "on-top-of"),) # b2 on top of b1
                    if debug: print("gRFL cond2:",("is", b2, b1, "on-top-of"))
            elif c1[0]==c2[0] and c1[2]==c2[2]: # if they are in the same x,z grid
                if c1[1]==c2[1]+1 or c1[1]==c2[1]-1:
                    new_st += (("is", b1, b2, "side-by-side"),) # b1 side by side with b2
                    if debug: print("gRFL cond3:",("is", b1, b2, "side-by-side"))
            elif c1[1]==c2[1] and c1[2]==c2[2]: # if they are in the same y,z grid
                if c1[0]==c2[0]+1 or c1[0]==c2[0]-1:
                    new_st += (("is", b1, b2, "side-by-side"),) # b1 side by side with b2
                    if debug: print("gRFL cond4:",("is", b1, b2, "side-by-side"))
    return tuple(set(new_st))

def getRelationsAndLocations(st):
    

    global start_state
    old_length = 0
    s_list = []
    s0 = st
    while old_length < len(s0):
        old_length = len(s0)
        s1_ = getLocationsFromRelations(s0)
        s1  = guessAndApplyWildcards(s1_)   
        s2_ = getRelationsFromLocations(s1)
        s0  = guessAndApplyWildcards(s2_)
    return s0


# <a id='WILDCARDS'></a>
# ### WILDCARDS

# In[23]:


def assignWildcard(state,wildcard,block):
    '''Changes all wildcard appereances for block'''
    return tuple (tuple(block if e==wildcard else e for e in tup) for tup in state)

#def defineWildcard(st, wildcard):
#    new_states = []
#    with HiddenPrints():
#        for b in getBlocks(st):
#            new_st = assignWildcard(st,wildcard,b)
#            if isValidState(new_st):
#                new_states = new_states + disambiguatedStates(new_st)
#    return list(set(new_states)) #return unique states

def getWildcards(st):
    '''Get a list of all wildcards'''
    wildcards = []
    for t in st:
        for e in t:
            if type(e)!=int and "wildcard" in e:
                wildcards.append(e)
    return list(set(wildcards))


# In[24]:


def guessWildcards(st):
    '''Returns a dictionary with wildcards as keys and possible block assigment as values'''
    wc = dict((w, []) for w in getWildcards(st))
            
    for w in wc.keys():
        oto = onTopOf(st,w)
        if oto:
            uno = underneathOf(st,oto)
            #print(w,"on top of",oto,"and",oto, "underneath",uno)
            if uno and w!=uno:
                wc[w] = uno[0] if "block" in uno[0] else uno[1]
    return wc

def applyDefinedWildcards(st, wc_dict):
    new_st = st
    for wildcard,guesses in wc_dict.items():
        if guesses: # in the future if I implement multiple guesses => len(guesses)==1:
            new_st = assignWildcard(new_st,wildcard,guesses)
    return tuple(set(new_st))

def guessAndApplyWildcards(st):
    return applyDefinedWildcards(st, guessWildcards(st))


# <a id='HIGH_LEVEL'></a>
# ### HIGH LEVEL

# In[25]:


def simplifyState(state):
    with HiddenPrints():
        for i in range(len(state)-1):
            new_state = state[:i] + state[i+1:]
            if isGoal(state, new_state):
                return simplifyState(new_state)
    return state


# In[26]:


def new_disambiguatedStates(st):
    global list_of_blocks
    states = []
    conflict_block = None
    
    old_length = 0
    s_list = []
    s0 = st
    while old_length < len(s0):
        old_length = len(s0)
        s1 = getRelationsAndLocations(s0)
        imp_cond, warnings = getRelationsFromRelations(s1)
        s2 = s1 + imp_cond
        s0 = getRelationsAndLocations(s2)
    return s0

    if warnings!=[]: #if warnings is not empty => ambiguous-state/not-well-defined-state
        conflict_block = warnings[0][0] #just mind for one warning..the other will be solve in recursive calls
        for b in list_of_blocks:
            if conflict_block != b:
                aux_state = new_st + (("is",conflict_block,b,"on-top-of"),)
                if isValidState(aux_state):
                    imp_cond2, warnings = getRelationsFromRelations(aux_state)
                    new_aux_state = aux_state + imp_cond2
                    if isValidState(new_aux_state):
                        if warnings==[]:
                            states.append(new_aux_state)
                        else:
                            new_states = disambiguatedStates(new_aux_state)
                            if new_states != []:
                                states += new_states
    else:
        states.append(new_st)
        
    states_ = []
    for s in states:
        if isValidState(s):
            states_.append(s)
            
    return removeDuplicates(states_)

def disambiguatedStates(st):
    global list_of_blocks
    states = []
    conflict_block = None

    imp_cond, warnings = getRelationsFromRelations(st)
    new_st = st + imp_cond
    
    if warnings!=[]: #if warnings is not empty => ambiguous-state/not-well-defined-state
        conflict_block = warnings[0][0] #just mind for one warning..the other will be solve in recursive calls
        for b in list_of_blocks:
            if conflict_block != b:
                aux_state = new_st + (("is",conflict_block,b,"on-top-of"),)
                if isValidState(aux_state):
                    imp_cond2, warnings = getRelationsFromRelations(aux_state)
                    new_aux_state = aux_state + imp_cond2
                    if isValidState(new_aux_state):
                        if warnings==[]:
                            states.append(new_aux_state)
                        else:
                            new_states = disambiguatedStates(new_aux_state)
                            if new_states != []:
                                states += new_states
    else:
        states.append(new_st)
        
    states_ = []
    for s in states:
        if isValidState(s):
            states_.append(s)
            
    return removeDuplicates(states_)


# In[27]:


def getOptimalState(start_st, all_goal_states):
    h_best = float('Inf')
    for gs in all_goal_states:
        h_candidate = hF(gs, start_st)
        if h_candidate < h_best:
            h_best = h_candidate
            best = gs
    return best


# In[28]:


def defineWildcards(start_state, st):
    '''Complete the goal state with wildcards and not-all-specified-relations-locations'''
    global list_of_blocks
    global global_coords
    global D
    #with HiddenPrints():
    new_states = [] #all new valid states
    wildcards = getWildcards(st)
    wc_length = len(wildcards)
    if wc_length:
        comb = []
        if nCr(len(list_of_blocks),wc_length) > 5000:
            wd = {}
            for t1 in st:
                try:
                    w_name = next(e for e in t1 if "wildcard" in e)
                    wd[w_name] = []
                    for t2 in start_state:
                        if len(t2)!=len(t1):continue
                        block_ = [y for x,y in zip(t1, t2) if x!=y]
                        if len(block_) == 1:
                            wd[w_name] =  wd[w_name].append(block_[0]) if wd[w_name] else [block_[0]]
                except:
                    continue

            aux_state = deepcopy(st)
            for w in wildcards:
                b_ = wd[w]
                if b_: b = b_[0]
                else:  b = np.random.choice(list_of_blocks) 
                aux_state = assignWildcard(aux_state,w,b)
            if isValidState(aux_state):
                new_states += disambiguatedStates(aux_state)
            
            timeout = time.time() + 30
            while True:
                if time.time() > timeout: break
                #blocks = np.random.choice(list_of_blocks, size=wc_length, replace=True)
                aux_state = deepcopy(st)
                for w in wildcards:
                    probability = 0.1 if wd[w] else 0.0
                    if np.random.random() > probability:
                        b = np.random.choice(list_of_blocks) 
                    else:
                        b = np.random.choice(wd[w])
                    aux_state = assignWildcard(aux_state,w,b)
                
                if isValidState(aux_state):
                    new_states += disambiguatedStates(aux_state) #TODO: maybe change it to getOptimalState
            
        else:
            #two diff wildcards can be assigned to the same block => comb_with_replacement
            for c in combinations_with_replacement(list_of_blocks, wc_length): 
                comb = comb + list(permutations(c))
            for c in comb:
                i = 0
                aux_state = deepcopy(st)
                for wc in wildcards:
                    aux_state = assignWildcard(aux_state,wc,c[i])
                    i += 1
                if isValidState(aux_state):
                    #new_states += disambiguatedStates(aux_state) #TODO: maybe change it to getOptimalState
                    new_states += [aux_state]
    else:
        new_states = [deepcopy(st)]
        
    isValid = False
    while not isValid:
        chosen_state = getOptimalState(start_state, list(set(new_states)))
        global_coords = getCoordinateRestrictions(chosen_state)    
        copy_global_coords = deepcopy(global_coords)

        defined_state = getRelationsAndLocations(chosen_state)  
        isValid = isValidState(defined_state)
        new_states.remove(chosen_state)

    while(global_coords!=copy_global_coords):
        copy_global_coords = deepcopy(global_coords)
        defined_state = getRelationsAndLocations(defined_state) 
    getFinalCoordinates(defined_state, start_state)
    defined_state = getRelationsAndLocations(tuple(set(defined_state)))    

    return defined_state


# <a id='LOW_LEVEL'></a>
# ### LOW LEVEL

# In[29]:


def isValidState(st):
    global list_of_blocks
    global global_coords
    global global_colors
    global D
    debug = D
    colors = getColors(st)
    for b in list_of_blocks:
        sbs = sideBySide(st,b)
        uno = underneathOf(st,b)
        oto = onTopOf(st,b)
        c_b = global_coords[b]

        if len(getCoordinates(st,b))>1: #you cannot have multiple locations in st
            if debug: print("Rejected by condition",1)
            return False
        if (len(sbs)>4) or (b in sbs):
            if debug: print("Rejected by condition",2)
            return False
        if (type(uno) is list) or (b == uno): # has more than 1 block underneath
            if debug: 
                print("Rejected by condition",3)
                print("Details")
                print("global_coords",global_coords)
                print("st",st)
            return False
        if (type(oto) is list) or (b == oto): # has more than 1 block on top
            if debug: print("Rejected by condition",4)
            return False
        if (uno in sbs) or (oto in sbs) or (oto==uno and oto!=None): # has to satisfy two uncompatible relationships
            if debug: print("Rejected by condition",5)
            return False
        if oto and oto!="table":
            cc_b = getCoordinates(st,b)
            if c_b!=[] and c_b[0][2]==0:
                if debug: print("Rejected by condition",6)
                return False
            if cc_b!=[] and cc_b[0][2]==0:
                if debug: print("Rejected by condition",7)
                return False
            c_oto = global_coords[oto]
            
            if c_oto!=[]:
                trues = [mayBeOnTop(cc[0],cc[1]) for cc in product(c_b,c_oto)]
                if trues:
                    if not any(trues): 
                        if debug: print("Rejected by condition",8)
                        return False 

        #  if c_oto!=[]:
        #      if c_oto!=[] and c_b!=[] and not any(mayBeOnTop(cc[0],cc[1]) for cc in product(c_b,c_oto)): #
        #          return False 

        # check from triples side-by-side loops A-B B-C C-A
        for bx in sbs:
            if set(sbs).intersection(set(sideBySide(st,bx))):
                if debug: print("Rejected by condition",9)
                return False
           
        if global_colors[b] != colors[b] and (global_colors[b] != "undefined" and colors[b] != "undefined"):
            if debug: print("Rejected by condition",10)
            return False
        
        
    # get list of blocks in different levels (by checking only onTop relations)
    pairs=[]
    for t in st:
        if "on-top-of" in t:
            pairs.append([t[1], t[2]])
    #print(pairs)
    # check if blocks in different levels are also in the same level (by checking sideByside relations)
    for p in pairs:
        for slb in getSameLevelBlocks(st):
            if len(set(p).intersection(slb))>1:
                if debug: 
                    print(set(p).intersection(slb))
                    print("Rejected by condition",11)
                return False
        
    for dlb in getDifferentLevelBlocks(st):
        for slb in getSameLevelBlocks(st):
            if len(dlb.intersection(slb))>1:
                if debug: print("Rejected by condition",12)
                return False
        
    return True


# In[30]:


def hF2(goal_state, state):
    return conditionsMet(goal_state, state).count(False)

def hF(goal_state, state):
    conditionsMet = []
    # simplified_goal = simplifyState(goal_state)
    h = 0
    show = False
    for condition in goal_state:
        if condition[0]=="has": continue #ignore attributes
        b1=condition[1]
        b2=condition[2]
        relation = condition[3]
        if (condition not in state):
            h += 1
            if show: print(condition)
            if ("on-top-of" in relation) and (underneathOf(state, b1) not in [None,"table"]):
                # add how many blocks need to be put above b1
                # h += getDepth(complete_goal, b1)
                # add how many blocks need to be taken from above to release b1
                # getDepth(complete_state, b1)
                h += 1 
                if show: print("extra cost for unstacking")     
        else: #can the condition be kept or should be broken to achieve other conditions?
            if ("on-top-of" in relation):
                b2_0 = onTopOf(goal_state, b2)
                if (b2_0 not in [None,"table"]):
                    if (b2_0 != onTopOf(state, b2)):
                        h += 1 
                        if show: print("extra cost for condition met but worthless")
                            
    final_clusters = getSameLevelBlocks(goal_state)
    current_clusters  = getSameLevelBlocks(state)
    longest = 0
    for fc in final_clusters:
        if not isClusterOnTable(goal_state,fc): continue
        for c in current_clusters:
            l = len(fc.intersection(c))
            if l>longest:
                longest = l 
        h += len(fc)-longest
    return h


# In[31]:


def conditionsMet(goal_state, state):
    conditionsMet = []
    for condition in goal_state:
        if "color" not in condition:
            conditionsMet.append(condition in state)
    return conditionsMet


# In[32]:


global global_coords
global list_of_blocks
global global_colors
global start_state

test_n=""
global D 
D = 0

try:
    startFile = open(sys.argv[1],"r")
    start_state = stateToTuple(list(x.rstrip() for x in startFile if x!='\n'))
    
    goalFile = open(sys.argv[2],"r")
    goal_state = stateToTuple(list(x.rstrip() for x in goalFile if x!='\n'))
except:
    print("error loading files")

list_of_blocks = getBlocks(start_state)
global_colors = getColors(start_state)
global_coords = getCoordinateRestrictions(goal_state)


defined_goal = defineWildcards(start_state, goal_state)


global_coords = getCoordinateRestrictions(start_state)
defined_start = getRelationsFromLocations(start_state)+getRelationsFromRelations(getRelationsFromLocations(start_state))[0]

start_filename = "tests/"+test_n+"start_defined"
goal_filename = "tests/"+test_n+"goal_defined"



printStateToFile(defined_start, start_filename)
printStateToFile(defined_goal, goal_filename)




