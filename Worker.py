from PyQt5.QtCore import QObject
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import PyQt5 as qt
import time

class Worker(QtCore.QThread):

    sig = QtCore.pyqtSignal(tuple)

    def __init__(self, vertices, lines, graph, parent=None):
        QtCore.QThread.__init__(self, parent)
        # self.is_running = True
        self.max_steps = len(lines)
        self.iteration = 0
        self.lines = lines
        self.graph = graph

    def on_source(self, payload):
        self.lines, self.iteration = payload[0], payload[1]

    def run(self):
        # if not self.is_running and self.iteration < self.max_steps:
        # 	self.is_running = True

        self.is_running = True

        while self.is_running and self.iteration < self.max_steps:
            # self.lines[self.graph.mst_indices[self.iteration]] = (255,0,0,255,1)
            if self.iteration in self.graph.mst_indices:
                self.lines[self.iteration] = (255,0,0,255,1)

            self.iteration += 1
            self.sig.emit((self.lines, self.iteration))
            time.sleep(.25)

        self.is_running = False

# class EdgeAnimation(QtCore.QThread):

#     def __init__(self,):
#         QtCore.QThread.__init__(self, parent)