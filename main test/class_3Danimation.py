#!/usr/bin/env python
# coding: utf-8


import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation
import matplotlib.colors as mpcolors


class Animation3D():

    def __init__(self):
        #self.fig = plt.figure()
        self.color_list = list(mpcolors._colors_full_map.values())
        self.fig = plt.figure(figsize=plt.figaspect(1))
        self.ax2 = self.fig.add_subplot(1, 1, 1, projection='3d')
        
        
        self.ax2.set_xticks(np.arange(0, 10, 1))
        self.ax2.set_yticks(np.arange(0, 10, 1))
        self.ax2.set_zticks(np.arange(0, 10, 1))
        
        
        
    def blocksOnTop(self, b1):
        c1 = self.coords[b1]
        blocks = []
        for b,c in self.coords.items():
            if c[0]==c1[0] and c[1]==c1[1] and c[2]>c1[2]:
                blocks.append(b)
        return blocks

    
  
        
        
    def update(self, i):
        
        voxels = np.empty(self.x.shape, dtype=bool)
        colors = np.empty(voxels.shape, dtype=object)
        first = True
        
        for block, coord in self.coords.items():
            cube = (self.x == coord[0]) & (self.y == coord[1]) & (self.z == coord[2])
            if self.color_dict == None:
                n_block = int(block.lstrip('block'))
                colors[cube] = self.color_list[n_block]
            else:
                colors[cube] = self.color_dict[block]
            if first:
                first = False
                voxels = cube
            else:
                voxels |= cube
        
        try:
            block_, coord_ = self.paths[i]
            #move also blocks on top
            blocks_on_top = self.blocksOnTop(block_)
            self.coords[block_] = coord_
            for b in blocks_on_top:
                c_old = self.coords[b]
                c_new = [coord_[0], coord_[1], c_old[2]]
                self.coords[b] = c_new
        except:
            print("")


        self.ax2.clear()  
        self.ax2.set_xticks(np.arange(0, 10, 1))
        self.ax2.set_yticks(np.arange(0, 10, 1))
        self.ax2.set_zticks(np.arange(0, 10, 1))
        self.ax2.voxels(voxels, facecolors=colors, edgecolor='k')   


    def plot(self, goal_coords, paths, coords, color_dict=None, speed=1000):
        
        self.paths = paths
        self.coords = coords
        self.goal_coords = goal_coords
        self.color_dict = color_dict

        self.x, self.y, self.z = np.indices((10, 10, 10))
        # plot goal
        # self.plotGoal()
        # plot solution
        self.ani = animation.FuncAnimation(self.fig, self.update, len(paths)+1, interval=speed, blit=False, repeat=False)
        plt.show()
   



