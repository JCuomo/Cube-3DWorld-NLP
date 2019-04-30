import math
import time
from itertools import product

class Astar_path():

    def isEmptyCoordinate(self, obstacles,xyz):
        if xyz in obstacles:
            return False
        return True

    def isValidCoordinate(self, xyz):
        x = xyz[0]
        y = xyz[1]
        z = xyz[2]
        if 0 <= x < 10 and 0 <= y < 10 and 0 <= z:
            return True
        return False

    def getDistance(self, c1,c2): #TODO: try Chebyschev
        return math.sqrt(sum([(a - b) ** 2 for a, b in zip(c1, c2)]))  

    def hF(self, goal_state, state):
        return self.getDistance(goal_state, state)

    class Node:
        def __init__(self, coordinates, f=0, g=0, h=0, parent=None):
            self.coordinates = coordinates
            self.f = f
            self.g = g
            self.h = h
            self.parent = parent

        def __hash__(self):
            return hash(self.coordinates)

        def __eq__(self, other):
            return (self.coordinates) == (other.coordinates)

        def __repr__(self):
            print(self.coordinates)
            return ""

    def isGoal(self, goal_xyz,xyz):
        return goal_xyz == xyz

    def getBestNode(self, nodeList):
        bestNode = nodeList[0]
        f = bestNode.f
        for node in nodeList:
            if node.f < bestNode.f:
                bestNode = node
        return bestNode

    def getChildren(self, xyz, obstacles, dim):
        ''' returns a list of valid children'''
        children = []
        
            
        for direction in list(product([-1,0,1], repeat=dim)):
            direction = list(direction)
            if all(v == 0 for v in direction): continue
            child = [sum(x) for x in zip(direction, xyz)]
            if dim==2:
                child = child+[0]
            if self.isEmptyCoordinate(obstacles, child) and self.isValidCoordinate(child):
                children.append(child)
        return children

    def AstarPath(self, start, goal, obstacles=None, dim=3):

        if obstacles==None:
            obstacles =[[]]
        if not self.isEmptyCoordinate(obstacles, goal) or not self.isValidCoordinate(goal):
            print("Destination occupied or invalid")
            return []
        
        if self.getChildren(goal, obstacles, dim)==[]:
            print("Destination blocked")
            return []
        
        h = self.hF(goal, start)
        start_node = Astar_path.Node(start, f=h, g=0, h=h)
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
            bestNode = self.getBestNode(unexpanded)
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
            children_coords = self.getChildren(bestNode.coordinates, obstacles, dim)
            if optim: print("Get children took: "+str(time.time()-t1))
            if debug: print("Children Nodes:")
            for child in children_coords:
                g = bestNode.g + 1 #TODO: Ithink I need to add + 1
                t1=time.time()
                h = self.hF(goal, child)
                if optim: print("Estimate H took: "+str(time.time()-t1))
                child_node = Astar_path.Node(child, f=g+h, g=g, h=h, parent=bestNode)
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
                if self.isGoal(goal, c.coordinates):
                    if debug: print("goal found, visiting "+str(path_length)+" nodes")
                    # Build the solution path as a list starting with goalState.
                    sol_node = c
                    while(sol_node):
                        solution.insert(0,sol_node)
                        sol_node = sol_node.parent
                    return solution, path_length
                if optim: print("Check goal took: "+str(time.time()-t1))
        print("goal not found: no more nodes to expand")
        return []

    def getDeltas(self, solution):
        prev = solution[0].coordinates
        delta = []
        for node in solution[1:]:
            coord = node.coordinates
            delta.append([coord[0]-prev[0],coord[1]-prev[1],coord[2]-prev[2]]) 
            prev = coord
        return delta

    def getCoords(self, solution):
        cs = []
        for node in solution[1:]:
            cs.append(node.coordinates) 
        return cs
    
    def AstarPathDelta(self, start, goal, obstacles=None, dim=3):
        solution, length = self.AstarPath(start, goal, obstacles, dim)
        return self.getDeltas(solution)
