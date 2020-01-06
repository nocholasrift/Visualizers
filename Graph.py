#Class to represent a graph 
#graph code from https://www.geeksforgeeks.org/
from scipy.spatial import Delaunay
import random
import PyQt5 as qt
import numpy as np

class Graph: 
  
    def __init__(self,num_vertices,num_edges): 

        self.V= num_vertices #No. of vertices 
        self.E = num_edges
        self.graph = [] # default dictionary  
                                # to store graph 
        self.mst = []

    # function to add an edge to graph 
    def addEdge(self,u,v,w):
        if [u,v,w] not in self.graph and [v,u,w] not in self.graph:
            self.graph.append([u,v,w]) 
  
    # A utility function to find set of an element i 
    # (uses path compression technique) 
    # modified to be iterative
    def find(self, parent, i):

        while parent[i] != i:
            i = parent[i]

        return i
  
    # A function that does union of two sets of x and y 
    # (uses union by rank) 
    def union(self, parent, rank, x, y):

        xroot = self.find(parent, x) 
        yroot = self.find(parent, y) 
  
        # Attach smaller rank tree under root of  
        # high rank tree (Union by Rank) 
        if rank[xroot] < rank[yroot]: 
            parent[xroot] = yroot 
        elif rank[xroot] > rank[yroot]: 
            parent[yroot] = xroot 
  
        # If ranks are same, then make one as root  
        # and increment its rank by one 
        else : 
            parent[yroot] = xroot 
            rank[xroot] += 1

    def kruskal(self):

        min_tree = []
        indices = []

        #Sort edges by weight
        edges = self.graph
        sorted_edges = sorted(self.graph, key=lambda edges: edges[2])

        num_edges = 0

        parent = [i for i in range(self.V)]
        rank = [0]*self.V

        i = 0

        # mst will have V - 1 edges
        # where V is number of vertices
        while num_edges < self.V - 1:
            u,v,w = sorted_edges[i]

            a = self.find(parent, u)
            b = self.find(parent, v)

            #if no cycle, add edge
            if a != b:
                num_edges += 1
                min_tree.append([u,v,w])
                indices.append(i)
                self.union(parent, rank, a, b)

            i += 1

        self.mst = min_tree
        self.mst_indices = indices
        return min_tree

    def generate_vertices(self):

        verts = []

        while len(verts) < self.V:
            coords = [int(random.random()*15 + .5),int(random.random()*15 + .5)]
            #TODO: Find something faster for this check
            if coords not in verts:
                verts.append(coords)

        return np.array(verts)

    def generate_edges(self,vertices):

        verts = vertices.tolist()
        #index 0 is indegree, index 1 is outdegree
        degrees = {}

        for v in verts:
            v.append(0)

        triangles = Delaunay(vertices)
        triangles = triangles.simplices

        for tri in triangles:
            self.addEdge(tri[0], tri[1], self.distance(vertices[tri[0]], vertices[tri[1]]))
            self.addEdge(tri[1], tri[2], self.distance(vertices[tri[1]], vertices[tri[2]]))
            self.addEdge(tri[2], tri[0], self.distance(vertices[tri[2]], vertices[tri[0]]))

        self.graph = sorted(self.graph, key=lambda edges: edges[2])

        self.kruskal()

        # ret_edges = list(self.mst)
        # shuffled_graph = random.sample(self.graph, len(self.graph))

        # for edge in shuffled_graph:
        #     if edge not in self.mst:
        #         ret_edges.append(edge)

        #     if len(ret_edges) == self.E:
        #         break

        return np.array([edge[:2] for edge in self.graph])

    def distance(self, v1, v2):
        return round(((v1[0]-v2[0])**2 + (v1[1]-v2[1])**2)**.5, 2)

def main():

    g = Graph(4)
    g.addEdge(0, 1, 10)
    g.addEdge(0, 2, 6)
    g.addEdge(0, 3, 5)
    g.addEdge(1, 3, 15)
    g.addEdge(2, 3, 4)

    mst = g.kruskal()
    
    for u,v,w in mst:
        print("%d -- %d == %d" % (u,v,w))


if __name__ == "__main__":
    main()