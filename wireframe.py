from functools import reduce
import numpy as np

class Wireframe:
    def __init__(self):
        self.nodes = np.zeros((0, 4))
        self.edges = []

    def addNodes(self, nodeArray):
        onesColumn = np.ones((len(nodeArray), 1))
        onesAdded = np.hstack((nodeArray, onesColumn))
        self.nodes = np.vstack((self.nodes, onesAdded))

    def addEdges(self, edgeList):
        self.edges += edgeList

    def transform(self, matrix):
        self.nodes = np.dot(self.nodes, matrix)

    def findCenter(self):
        num_nodes = len(self.nodes)
        return tuple(n/num_nodes for n in reduce(
            lambda sum, node: (
                sum[0] + node.x,
                sum[1] + node.y,
                sum[2] + node.z
            ),
            self.nodes,
            (0,0,0)
        ))

    def outputNodes(self):
        print('\n --- Nodes --- ')
        for i, (x, y, z, _) in enumerate(self.nodes):
            print(f' {i}: ({x}, {y}, {z})')

    def outputEdges(self):
        print('\n --- Edges --- ')
        for i, (node1, node2) in enumerate(self.edges):
            print(f' {i}: {node1} to {node2}')
