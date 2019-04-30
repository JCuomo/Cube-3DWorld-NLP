#!/usr/bin/env python
# coding: utf-8

# In[1]:

get_ipython().run_line_magic('reset', "-f")

from copy import deepcopy 
import sys, os
import time
class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


# In[2]:


def stateToTuple(state):
    state_tuples = []
    for line in state:
        s_parts = line.split(" ")
        modifier = s_parts[0].replace("(","")
        b1 = s_parts[1]
        if(modifier=="has"): 
            property_name = s_parts[2]      
            property_value = s_parts[3].replace(")","")
            state_tuples.append((modifier,b1,property_name,property_value))
        elif(modifier=="is"):
            b2 = s_parts[2]      
            relation = s_parts[3].replace(")","")  
            state_tuples.append((modifier,b1,b2,relation))
    return tuple(state_tuples)


# In[3]:


def getBlocks(st):
    blocks = []
    for t in st:
        for e in t:
            if "block" in e:
                blocks.append(e)
    return list(set(blocks))

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


# In[4]:


class Node:
    def __init__(self, state, f=0, g=0, h=0, parent=None, move=None):
        self.state = state
        self.f = f
        self.g = g
        self.h = h
        self.parent = parent
        self.move = move
        
    def __hash__(self):
        return hash(self.state)

    def __eq__(self, other):
        return (self.state) == (other.state)
        
    def __repr__(self):
        if self.move:
            printCommand(self.move)
        #printState(self.state)
        return ""


# In[5]:


def conditionsMet(goal_state, state):
    conditionsMet = []
    for condition in goal_state:
        if "on-top-of" in condition: #condition[0]!="has":
            conditionsMet.append(condition in state)
    return conditionsMet

def isGoal(goal_state, state):
    return all(conditionsMet(goal_state,state))


# In[6]:


def hF2(goal_state, state):
    return conditionsMet(goal_state, state).count(False)

def hF(goal_state, state):
    conditionsMet = []
    # simplified_goal = simplifyState(goal_state)
    h = 0
    show = False
    for condition in goal_state:
        b1=condition[1]
        b2=condition[2]
        relation = condition[3]
        #if "color" in condition:
         #   continue
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
    return h


# In[7]:


def isValidState(st):
    for b in list_of_blocks:
        uno = underneathOf(st,b)
        oto = onTopOf(st,b)
        
        if (type(uno) is list) or (b == uno): # has more than 1 block underneath
            return False
        if (type(oto) is list) or (b == oto): # has more than 1 block on top
            return False
        if oto==uno and oto!=None: # has to satisfy two uncompatible relationships
            return False    
    return True


# In[8]:


def genCommand(action, b1_id, b2_id):
    return (action, b1_id, b2_id)

def printCommand(command):
    if command:
        print("("+command[0]+" "+command[1]+" "+command[2]+")")


def printState(state):
    for t in state:
        #final version: print("("+t[0]+" "+t[1]+" "+t[2]+" "+t[3]+")")
        #print(t[1]+" "+t[3]+" "+t[2])
        print(t)


# In[9]:


def getBestNode(nodeList):
    bestNode = nodeList[0]
    for node in nodeList:
        if node.f < bestNode.f:
            bestNode = node
        elif node.f == bestNode.f and node.g > bestNode.g:
            bestNode = node
        elif node.f == bestNode.f and node.g == bestNode.g: 
            if node.move:
                action = node.move[0]
                b1 = node.move[1]
                t = node.move[2]
                if action=="stack" and t=="table":
                    bestNode = node
    return bestNode

def isValid(state, command):
    action = command[0]
    b1 = command[1]
    b2 = command[2]
    if b1 == "table":
        return false
    if action == "stack": # neither block has other blocks on top
        if (not underneathOf(state, b1)) and ((not underneathOf(state, b2)) or (b2 == "table")):
            return True
        
    return False

def isWise(state, command, goal_state):
    action = command[0]
    b1 = command[1]
    b2 = command[2]
    if action == "stack": 
        if b2 != "table":
            if onTopOf(goal_state,b1)=="table":
                # if I want to stack b1 on top of something that's not the table 
                # and in the goal state it's on the table I shouldn't do it
                return False
        if onTopOf(goal_state,b1)!=b2 and b2 != "table":
            # don't stack blocks on each other if they don't need to be..use the table
            return False
        if ("is",b1,b2,"on-top-of") in state:
            # if the action led to a state that already exist don't waste energy
            return False
        
    return True


# In[10]:


def getCommands(node, actions, goal_state):
    ''' return a list of valid commands'''
    cmds = []
    # test all combinations of blocks and commands
    for block1 in list_of_blocks:
        for block2 in list_of_blocks + ['table']:
            if block1 == block2:
                continue
            for action in actions:
                cmd = genCommand(action, block1, block2)
                # only add those actions that are valid and wise
                if isValid(node.state, cmd) and isWise(node.state, cmd, goal_state): 
                    cmds.append(cmd)
    return cmds

def applyCommand(node, command):
    action = command[0]
    b1 = command[1]
    b2 = command[2]
    if action == "stack": 
        #clear all previous relationships that will not longer exist after the move
        new_state = tuple(x for x in node.state if not (b1==x[1] and "on-top-of" in x))
        #add new relationship directly created by the move
        return new_state + (("is",b1,b2,"on-top-of"),)
    return

def actionCost(command):
    action = command[0]
    if action == "stack": 
        return 1
    return float('inf')


# In[11]:


def overlapRelations(st, relation):
    ''' Given the relation -, then if (a-b) and (b-c) the output will be (a,b,c)'''
    pairs=[] 
    for t in st:
        if relation in t:
            if t[1] == "table" or t[2] == "table": continue 
            pairs.append([t[1], t[2]])

    # merge pairs with common blocks
    out = []
    while len(pairs)>0:
        first, *rest = pairs
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
        pairs = rest
    return out

def getDifferentLevelBlocks(st):
    '''returns towers'''
    return overlapRelations(st, "on-top-of")


# In[12]:


def Astar(start_state, goal_state):
    
    global list_of_blocks
    list_of_blocks = getBlocks(start_state)
    
    if not isValidState(start_state):
        print("Invalid start state")
        return None,None
    elif not isValidState(goal_state):
        print("Invalid goal state")
        return None,None
        
    h = hF(goal_state, start_state)
    start_node = Node(state=start_state, f=0+h, g=0, h=h)
    actions = ["stack"]
    solution = []
    debug = 0
    optim = False
    path_length = 0
    bestNode = None
    # Initialize expanded to be an empty dictionary
    expanded = []
    # Initialize unExpanded to be a list containing the startState node. Its h value is calculated using hF, its g value is 0, and its f value is g+h.
    #unexpanded = [( start_node, None)]
    unexpanded = [start_node]
    # If startState is the goalState, return the list containing just startState and its f value to debug the cost of the solution path.
    if isGoal(goal_state, start_node.state):
        if debug: print("goal found, visiting "+str(path_length)+" nodes")
        solution.insert(0,start_node)
        return solution, 1
    # Repeat the following steps while unExpanded is not empty:
    while(unexpanded):  
        #print("unexpanded")
        #print(unexpanded)
        #print("expanded")
        #print(expanded)        
        children = []
        # Pop from the front of unExpanded to get the best (lowest f value) node to expand.
        t1=time.time()
        bestNode = getBestNode(unexpanded)
        if optim: print("Finding best node took: "+str(time.time()-t1))
        path_length += 1
        unexpanded.remove(bestNode)
        if debug or 0: 
            print("##### BEST NODE #####:")
            #print(bestNode.parent)
            print("g:"+str(bestNode.g)+", h:"+str(bestNode.h)+", f:"+str(bestNode.f))
            print(bestNode)
        # Generate the children of this node.
        t1=time.time()
        commands = getCommands(bestNode, actions, goal_state)
        if optim: print("Get commands took: "+str(time.time()-t1))
        
        if debug: print("Children Nodes:")
        for cmd in commands:
            t1=time.time()
            child_state = applyCommand(bestNode, cmd)
            if optim: print("Applied cmds took: "+str(time.time()-t1))
            g = bestNode.g + actionCost(cmd)
            t1=time.time()
            h = hF(goal_state, child_state)
            if optim: print("Estimate H took: "+str(time.time()-t1))
            #print("H: "+str(h)+", H2: "+str(h2))
            #if(h>h2):
                #print(child_state)
            child_node = Node(child_state, f=g+h, g=g, h=h, parent=bestNode, move=cmd)
            if debug: 
                print("g:"+str(g)+", h:"+str(h)+", f:"+str(g+h))
                print(child_node)
            children.append(child_node)
        # Add the node to the expanded dictionary, indexed by its state.
        expanded.append(bestNode)
        # Remove from children any nodes that are already either in expanded or unExpanded, unless the node in children has a lower f value.
        t1=time.time()
        for c in children:
            if c in expanded:
                if expanded[expanded.index(c)].f < c.f:
                    if debug: 
                        print("remove from children cause expanded has better")   
                        #print(c)
                    children.remove(c)
                else:
                    expanded.remove(c)
                    if debug: 
                        print("remove from expanded")
                        #print(c)
            elif c in unexpanded:
                if unexpanded[unexpanded.index(c)].f < c.f:
                    if debug: 
                        print("remove from children cause unexpanded has better")     
                        #print(c)
                    #children.remove(c) #I don't need to remove it, just don't add it to unexpanded..
                    # besides I cannot modified the list I'm iterating
                else:
                    unexpanded.remove(c)
                    if debug: 
                        print("remove from unexpanded")
                        #print(c)
            else: # Insert the modified children list into the unExpanded list and ** sort by f values.**
                if debug: print("new child")
                unexpanded.insert(0,c)
            if optim: print("Adjust unexp and exp took: "+str(time.time()-t1))    
            t1=time.time()
            # If goalState is in children:
            if isGoal(goal_state, c.state):
                if debug: print("goal found, visiting "+str(path_length)+" nodes")
                # Build the solution path as a list starting with goalState.
                sol_node = c
                while(sol_node):
                    solution.insert(0,sol_node)
                    sol_node = sol_node.parent
                return solution, path_length
            if optim: print("Check goal took: "+str(time.time()-t1))
    print("goal not found: no more nodes to expand")
    return expanded, unexpanded


# In[13]:


#sys.argv[1] = "tests/1start_defined"
#sys.argv[2] = "tests/1goal_defined"


# In[14]:
test_n = ""

start_filename = "tests/"+test_n+"start_defined"
goal_filename = "tests/"+test_n+"goal_defined"


try:
    startFile = open(start_filename,"r")
    goalFile = open(goal_filename,"r")
    
    start_state = stateToTuple(list(x.rstrip() for x in startFile))
    goal_state = stateToTuple(list(x.rstrip() for x in goalFile))
except:
    sys.exit("error loading files")


e,u = Astar(start_state, goal_state)

with open("tests/"+test_n+"relations", 'w') as f:
    for t in e:
        command = t.move
        if command:
            print("("+command[0],command[1],command[2]+")", file=f)
