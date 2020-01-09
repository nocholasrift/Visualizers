from PyQt5.QtCore import QObject
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import PyQt5 as qt
import time


class Worker(QtCore.QThread):

    sig = QtCore.pyqtSignal(tuple)

    def __init__(
        self, vertices, lines, graph, parent=None, default_col=None, mst_col=None
    ):
        QtCore.QThread.__init__(self, parent)
        # self.is_running = True
        self.max_steps = len(lines)
        self.iteration = 0
        self.lines = lines
        self.graph = graph
        self.DEFAULT_EDGE_COLOR = (
            (255, 255, 255, 32, 1) if not default_col else default_col
        )
        self.MST_EDGE_COLOR = (255, 191, 0, 255, 1) if not mst_col else mst_col

    def on_source(self, payload):
        self.lines, self.iteration = payload[0], payload[1]

    def run(self):

        self.is_running = True

        while self.is_running and self.iteration < self.max_steps:
            # self.lines[self.graph.mst_indices[self.iteration]] = (255,0,0,255,1)
            if self.iteration in self.graph.mst_indices:
                self.lines[self.iteration] = self.MST_EDGE_COLOR  # (255,0,0,255,1)
            else:
                self.lines[self.iteration] = self.DEFAULT_EDGE_COLOR

            self.iteration += 1
            self.sig.emit((self.lines, self.iteration))
            time.sleep(0.25)

        self.is_running = False


class EdgeAnimation(QtCore.QThread):

    sig = QtCore.pyqtSignal(tuple)

    # def __init__(self, edge, pos, adj, brush, lines, size, pxMode):
    def __init__(self, edge, edge_color, steps=None, higlight_color=None):
        QtCore.QThread.__init__(self, parent)
        # self.edge = edge
        # self.pos = pos
        # self.adj = adj
        # self.brush = brush
        # self.lines = lines
        # self.size = size
        # self.pxMode = pxMode

        self.edge_color = edge_color
        self.higlight_color = higlight_color if higlight_color else (255, 0, 0, 255, 1)
        self.steps = steps if steps else 15

    def on_source(self, payload):
        self.edge, self.edge_color = payload[0], payload[1]

    def run(self):

        self.is_running = True
        # s = 1
        dr = (self.higlight_color[0] - self.edge_color[0]) / self.steps
        dg = (self.higlight_color[1] - self.edge_color[1]) / self.steps
        db = (self.higlight_color[2] - self.edge_color[2]) / self.steps
        da = (self.higlight_color[3] - self.edge_color[3]) / self.steps

        deltas = [dr, dg, db, da]
        channels = [color[:4] for color in self.edge_color]
        # True indicates going TO target color
        direction = True

        while self.is_running:

            count = 0
            for item in enumerate(channels):

                channel, ind = item[1], item[0]
                if channel < 255:
                    channel += deltas[ind]
                    if channel > 255:
                        channel = 255
                else:
                    count += 1

            if count == 4:
                for delta in deltas:
                    delta *= -1
