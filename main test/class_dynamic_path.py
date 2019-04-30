import math
import time
from itertools import product
from copy import deepcopy
from scipy.spatial.distance import pdist
from itertools import chain 
import class_Astar_path as pathFinder
import sys, os
import numpy as np

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
        
        
class Astar_dynamic_path():

    def isEmptyCoordinate(self, state,xyz):
        return not xyz in state.values()
    
    def isValidCoordinate(self, xyz):
        x = xyz[0]
        y = xyz[1]
        z = xyz[2]
        if 0 <= x < 10 and 0 <= y < 10 and 0 <= z:
            return True
        return False

    def getDistance(self, c1,c2):
        return int(pdist([c1,c2], 'chebyshev')[0])

    def hF2(self, goal_state, state): #basic but works
        total_length = 0
        for b,c in state.items():
            total_length += self.getDistance(goal_state[b], c)            
        return total_length

    def hF1(self, goal_state, state):
        total_length = 0
        for b,c in state.items():
            dest = goal_state[b]
            if c[2]!=0 or dest[2]!=0: continue
            total_length += self.getDistance(dest, c)
            for step in self.getGridsFromAtoB(dest,c):
                if not self.isEmptyCoordinate(state,step):
                    total_length += 1
            #print("distance to goal:",b,self.getDistance(goal_state[b][0], c[0]))
        return total_length
 
    def hF3(self, goal_state, state):
        total_length = 0
        for b,c in state.items():
            dest = goal_state[b]
            if c[2]!=0 or dest[2]!=0: continue
            total_length += self.getDistance(c, dest)
            total_length += self.addPenalties(c, dest, state)
            #print("distance to goal:",b,self.getDistance(goal_state[b][0], c[0]))
        return total_length
    
    def hF4(self, goal_state, state):
        total_length = 0
        for b,c in state.items():
            dest = goal_state[b]
            if c[2]!=0 or dest[2]!=0: continue
            total_length += self.getDistance(dest, c)
            total_length += self.add(c, dest, state)  
            #print("distance to goal:",b,self.getDistance(goal_state[b][0], c[0]))
        return total_length


    def hF(self, goal_state, state): #best one for unlocking blocks
        total_length = 0
        for b,c in state.items():
            dest = goal_state[b]
            if c[2]!=0 or dest[2]!=0: continue
            if c==dest: continue
            total_length += self.getDistance(dest, c)
            for step in self.getGridsFromAtoB(dest,c):
                if not self.isEmptyCoordinate(state,step):
                    total_length += sum(range(len(self.getGridsFromAtoB(step, dest))+1))
        return total_length
    
    def add(self, orig, dest, state):
        total_length = 0
        for step in self.getGridsFromAtoB(orig, dest):
            total_length += 1
            if not self.isEmptyCoordinate(state,step):
                total_length += 1
                total_length += self.add(step, dest, state)
        return total_length
    
    def getClosestEmptyGrid(self, orig, state):
        X = self.getDistanceMap(orig, orig, 2)
        while(1):
            m = divmod(X.argmin(), X.shape[1])
            m_ = [m[0],m[1],0]
            if self.isValidCoordinate(m_) and self.isEmptyCoordinate(state,m_):
                return m_
            else:
                X[m] = np.inf

    def addPenalties(self, orig, dest, state):
        path = self.getGridsFromAtoB(orig, dest) #TODO: improve searching the path tunneling less obstacles
        obstacles = state
        i = 0
        for step in path:
            obstacles[i]=step
            i += 1
  
        total_length = 0
        for step in path:
            if not self.isEmptyCoordinate(state,step):
                total_length += 1
                total_length += self.addPenalties(step, self.getClosestEmptyGrid(step, obstacles), state)
        return total_length       
                
    def getDistanceMap(self, orig, dest, k):
        orig = orig[:2]
        dest = dest[:2]
        i_coords, j_coords = np.meshgrid(range(10), range(10), indexing='ij')
        M = np.array([i_coords, j_coords])
        D = np.zeros(shape=(10,10))
        shortest_distance = self.getDistance(orig, dest)
        for i in range(10):
            for j in range(10):
                #S[i,j] = getDistance(M[:,i,j],b)
                D[i,j] = self.getDistance(M[:,i,j],dest) + k*self.getDistance(M[:,i,j],orig) - shortest_distance  
        return D        
                    
    def getGridsFromAtoB(self, xyzA,xzyB):
        with HiddenPrints():
            pf = pathFinder.Astar_path()
            path_nodes,_ = pf.AstarPath(xyzA, xzyB, None, 2)
            solution = []
            for p in path_nodes:
                solution.append(p.coordinates)
        return solution

    class Node:
        def __init__(self, coordinates, f=0, g=0, h=0, parent=None, move=None):
            self.coordinates = coordinates
            self.f = f
            self.g = g
            self.h = h
            self.parent = parent
            self.move = move

        def __hash__(self):
            return hash(self.coordinates)

        def __eq__(self, other):
            return (self.coordinates) == (other.coordinates)

        def __repr__(self):
            print(self.move)
            return ""

    def isGoal(self, state, goal):
        return state == goal

    def getBestNode2(self, nodeList):
        bestNode = nodeList[0]
        for node in nodeList:
            if node.f < bestNode.f:
                bestNode = node
            elif node.f == bestNode.f and node.g > bestNode.g:
                bestNode = node  
        return bestNode
    
    def getBestNode(self, nodeList, prevNode):
        if prevNode and prevNode.move:
            prevB = prevNode.move[0]
        bestNode = nodeList[0]
        for node in nodeList:
            if node.f < bestNode.f:
                bestNode = node
            elif node.f == bestNode.f and node.g > bestNode.g:
                bestNode = node  
            elif node.f == bestNode.f and node.g > bestNode.g and node.move[0]==prevB:
                bestNode = node 
        return bestNode
    
    def getChildren(self, state, dim):
        ''' returns a list of valid children'''
        children = []
        directions = list(product([-1,0,1], repeat=dim))
        for b,c in state.items():    
            if c[2]!=0: continue
            for direction in directions:
                direction = list(direction)
                if all(v == 0 for v in direction): continue
                new_c = [sum(x) for x in zip(direction, c)]
                
                if dim==2:
                    new_c = new_c+[0]
               # new_c = tuple(new_c)    
                if self.isValidCoordinate(new_c) and self.isEmptyCoordinate(state, new_c):
                    if -1 in new_c:
                        print(new_c)
                    children.append((b,new_c))

        return children

    def AstarPath(self, start_, goal_, dim=2):
        start={}
        goal={}
        for b,c in start_.items():
            if c[2]==0:
                start[b]=c
        for b,c in goal_.items():
            if c[2]==0:
                goal[b]=c                
        
        h = self.hF(goal, start)
        start_node = Astar_dynamic_path.Node(start, f=h, g=0, h=h)
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
        if self.isGoal(goal, start_node.coordinates):
            print("goal found: visiting "+str(path_length)+" nodes")
            solution.insert(0,start_node)
            return solution, 1
        # Repeat the following steps while unExpanded is not empty:
        while(unexpanded):  
            #print(unexpanded)
            #print("expanded")
            #print(expanded)        
            children = []
            # Pop from the front of unExpanded to get the best (lowest f value) node to expand.
            t1=time.time()
            bestNode = self.getBestNode(unexpanded, bestNode)
            if optim: print("Finding best node took: "+str(time.time()-t1))
            path_length += 1
            unexpanded.remove(bestNode)
            if debug or 0: 
                print("##### BEST NODE #####:")
                #print(bestNode.parent)
                print("g:"+str(bestNode.g)+", h:"+str(bestNode.h)+", f:"+str(bestNode.f))
                print(bestNode)
            # Generate the children of self node.
            t1=time.time()
            children_move = self.getChildren(bestNode.coordinates, dim)
            if optim: print("Get children took: "+str(time.time()-t1))
            if debug: print("Children Nodes:")
            for move in children_move:
                g = bestNode.g + 1 
                t1=time.time()
                if optim: print("Estimate H took: "+str(time.time()-t1))
                child_coords = deepcopy(bestNode.coordinates)
                child_coords[move[0]] = move[1]
                if path_length > 1000: #if is taking too long use a more agresive heuristic
                    h = self.hF(goal, child_coords)
                else:
                    h = self.hF(goal, child_coords)
                child_node = Astar_dynamic_path.Node(child_coords, f=g+h, g=g, h=h, parent=bestNode, move=move)
                if debug: 
                    print("g:"+str(g)+", h:"+str(h)+", f:"+str(g+h))
                    print(child_node)
                children.append(child_node)
            # Add the node to the expanded dictionary, indexed by its state.
            expanded.append(bestNode)
            # Remove from children any nodes that are already either in expanded or unExpanded, unless the node in children has a lower f value.
            t1=time.time()
            children_ = deepcopy(children)
            for c in children_:
                if c in expanded:
                    if expanded[expanded.index(c)].f < c.f:
                        if debug: 
                            print("remove from children cause expanded has better")   
                            print(c)
                        children.remove(c)
                    else:
                        expanded.remove(c)
                        if debug: 
                            print("remove from expanded")
                            print(c)
                elif c in unexpanded:
                    if unexpanded[unexpanded.index(c)].f < c.f:
                        if debug: 
                            print("remove from children cause unexpanded has better")     
                            print(c)
                        #children.remove(c) #I don't need to remove it, just don't add it to unexpanded..
                        # besides I cannot modified the list I'm iterating
                    else:
                        unexpanded.remove(c)
                        if debug: 
                            print("remove from unexpanded")
                            print(c)
                else: # Insert the modified children list into the unExpanded list and ** sort by f values.**
                    if debug: print("new child")
                    unexpanded.insert(0,c)
                if optim: print("Adjust unexp and exp took: "+str(time.time()-t1))    
                t1=time.time()
                # If goalState is in children:
                if self.isGoal(goal, c.coordinates):
                    print("goal found, visiting "+str(path_length)+" nodes")
                    # Build the solution path as a list starting with goalState.
                    sol_node = c
                    while(sol_node):
                        solution.insert(0,sol_node)
                        sol_node = sol_node.parent
                    return solution, path_length
                if optim: print("Check goal took: "+str(time.time()-t1))
        print("goal not foundA: no more nodes to expand")
        return expanded, unexpanded

    def getDeltas(self, solution):
        delta = []
        for node in solution[1:]:
            block = node.move[0]
            prev = node.parent.coordinates[block]
            coord = node.move[1]
            delta.append((block,[coord[0]-prev[0],coord[1]-prev[1],coord[2]-prev[2]])) 
        return delta

    def AstarPathDelta(self, start, goal, obstacles=None, dim=3):
        solution, length = self.AstarPath(start, goal)
        return self.getDeltas(solution)
 
