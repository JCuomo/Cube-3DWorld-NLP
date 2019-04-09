#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import copy
import class_3Danimation as anim
get_ipython().run_line_magic('matplotlib', 'notebook')

class PlotSolution():
    
    def cmdToTuple(self, st_txt):
        st_t = (tuple(line[1:-1].split(" ")) for line in st_txt)
        return list(tuple(int(x) if x.lstrip('-').isdigit() else x for x in t if x!="command") for t in st_t)

    def getCoordinates(self, st, block=None):
        if block:    
            for t in st:
                if ("location" in t) and (block in t):
                    return list(t[3:6])
            return []
        else:
            coords = dict()
            for b in self.getBlocks(st):
                coords[b] = self.getCoordinates(st, b)
            return coords

    def getBlocks(self, st):
        blocks = []
        for t in st:
            for e in t:
                if type(e)!=int and "block" in e:
                    blocks.append(e)
        return list(set(blocks))

    def cmdsToPaths(self, initial_coords, cmds):
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
    
    def getColors(self, st, block=None):
        if block:    
            for t in st:
                if ("color" in t) and (block in t):
                    return t[3]
            return "white"
        else:
            colors = dict()
            for b in self.getBlocks(st):
                colors[b] = self.getColors(st, b)
            return colors


    def plot(self, test_n, fps=10):
        
        start_filename = "tests/"+test_n+"start_defined"
        goal_filename = "tests/"+test_n+"goal_defined"
        cmds_filename = "tests/"+test_n+"paths"

        startFile = open(start_filename,"r")
        start_state = self.cmdToTuple(list(x.rstrip() for x in startFile))
        
        goalFile = open(goal_filename,"r")
        goal_state = self.cmdToTuple(list(x.rstrip() for x in goalFile))

        cmdsFile = open(cmds_filename,"r")
        cmds = self.cmdToTuple(list(x.rstrip() for x in cmdsFile))
        paths = self.cmdsToPaths(self.getCoordinates(start_state), cmds)
        
        self.color_dict = self.getColors(start_state)

        p = anim.Animation3D()
        p.plot(self.getCoordinates(goal_state), paths, self.getCoordinates(start_state), self.color_dict, fps)
        self.paths=paths

