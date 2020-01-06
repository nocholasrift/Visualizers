# -*- coding: utf-8 -*-
"""
Simple example of GraphItem use.
"""

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QLabel,
)
import PyQt5 as qt
import numpy as np
import Graph
import Worker
import time

NUM_VERTICES = 30
# Must be at least NUM_VERTICES - 1
NUM_EDGES = 0


class Window(QMainWindow):

    sig = QtCore.pyqtSignal(object)

    def __init__(self):

        super(Window, self).__init__()
        self.setGeometry(50, 50, 1024, 760)
        self.setWindowTitle("Kruskal Visualization")
        self.setWindowIcon(QtGui.QIcon("pythonlogo.png"))

        # initialize graph configurations
        self.lines = []
        self.pos = []
        self.adj = []
        self.g = ""
        self.PIXEL_MODE = True
        self.SIZE = 10
        self.graph = Graph.Graph(NUM_VERTICES, NUM_EDGES)

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.black)
        self.setPalette(p)

        self.layout = QVBoxLayout()

        self.graph_layout = QHBoxLayout()
        self.graph_layout.addWidget(self.home())

        self.edge_table = QVBoxLayout()

        self.edge_table_label = QLabel("V 1\tV 2\tCost")
        self.edge_table_label.setObjectName('edge_table_label')
        self.edge_table_label.setStyleSheet('QLabel#edge_table_label {color: white}')
        self.edge_table_label.hide()
        self.edge_table.addWidget(self.edge_table_label)

        self.edge_label_array = []

        for i in range(5):
            edge = self.graph.graph[i]
            label_str = str(edge[0]) + "\t" + str(edge[1]) + "\t" + str(edge[2])
            tmp = QLabel(label_str)
            tmp.setObjectName('tmp')
            tmp.setStyleSheet('QLabel#tmp {color: white}')
            tmp.hide()
            self.edge_label_array.append(tmp)
            self.edge_table.addWidget(tmp)

        self.graph_layout.addLayout(self.edge_table)

        # self.b2 = QPushButton("Begin")
        # layout.addWidget(self.home())
        self.layout.addLayout(self.graph_layout)

        self.b1 = QPushButton("Start")
        self.b1.clicked.connect(self.start)
        self.layout.addWidget(self.b1)

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

    def home(self):

        global NUM_EDGES
        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)

        w = pg.GraphicsWindow()
        w.setWindowTitle("Graph Visualization")
        v = w.addViewBox()
        v.setAspectLocked()

        self.g = pg.GraphItem()
        v.addItem(self.g)

        # Define positions of nodes
        self.pos = self.graph.generate_vertices()
        """np.array([
            [0,0],
            [10,0],
            [0,10],
            [10,10],
            [5,5],
            [15,5]
            ])"""

        # Define the set of connections in the graph
        self.adj = self.graph.generate_edges(self.pos)
        """np.array([
            [0,1],
            [1,3],
            [3,2],
            [2,0],
            [1,5],
            [3,5],
            ])"""

        NUM_EDGES = len(self.adj)

        self.mst = []
        for edge in self.graph.mst:
            self.mst.append(edge[:2])

        # Define the symbol to use for each node (this is optional)
        # symbols = ['o','o','o','o','t','+']

        # Define the line style for each connection (this is optional)
        self.lines = np.array(
            ([(255, 255, 255, 0, 1) for e in self.adj]),
            dtype=[
                ("red", np.ubyte),
                ("green", np.ubyte),
                ("blue", np.ubyte),
                ("alpha", np.ubyte),
                ("width", float),
            ],
        )

        self.V_COLOR = (255, 255, 255, 255)
        self.V_COLOR_OFF = (255, 255, 255, 0)

        # Update the graph
        # size is 0 so vertice outlines don't show initially
        self.g.setData(
            pos=self.pos,
            adj=self.adj,
            brush=self.V_COLOR_OFF,
            pen=self.lines,
            size=0,
            pxMode=self.PIXEL_MODE,
        )

        return w

    def start(self):

        self.iteration = 0

        # setup thread
        self.thread = Worker.Worker(NUM_VERTICES, self.lines, self.graph)
        self.sig.connect(self.thread.on_source)
        self.sig.emit((self.lines, self.iteration))
        self.thread.is_running = False

        # setup buttons
        self.b1.hide()
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next)
        self.prev_button = QPushButton("Back")
        self.prev_button.clicked.connect(self.prev)
        self.play_button = QPushButton("Play")
        self.prev_button.setEnabled(False)
        self.play_button.clicked.connect(self.play)
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause)
        self.pause_button.hide()
        self.button_array = QHBoxLayout()
        self.button_array.addWidget(self.prev_button)
        self.button_array.addWidget(self.play_button)
        self.button_array.addWidget(self.pause_button)
        self.button_array.addWidget(self.next_button)
        self.layout.addLayout(self.button_array)

        # animations
        self.fade_in()
        self.highlight_edge(self.iteration)
        # Labels
        #TODO: Add animation for labels
        self.edge_table_label.show()
        for i in range(len(self.edge_label_array)):
            self.edge_label_array[i].show()

    def stop_thread():

        self.worker.stop()
        self.thread.quit()
        self.thread.wait()

    def next(self):

        if self.iteration == NUM_EDGES - 1:
            self.next_button.setEnabled(False)

        self.prev_button.setEnabled(True)

        #self.lines[self.graph.mst_indices[self.iteration]] = (255, 0, 0, 255, 1)
        #print(self.graph.mst_indices)
        if self.iteration in self.graph.mst_indices:
            self.lines[self.iteration] = (255,0,0,255,1)
        else:
            self.lines[self.iteration] = (255,255,255,32,1)

        self.g.setData(
            pos=self.pos,
            adj=self.adj,
            brush=self.V_COLOR,
            pen=self.lines,
            size=self.SIZE,
            pxMode=self.PIXEL_MODE,
        )
        pg.QtGui.QApplication.processEvents()
        self.iteration += 1
        self.update_edge_list(direction=False)
        self.highlight_edge(self.iteration)

        # Need to signal thread of changes to lines and iteration
        self.sig.emit((self.lines, self.iteration))

    def prev(self):

        self.lines[self.iteration] = (255,255,255,32,1)
        self.g.setData(
            pos=self.pos,
            adj=self.adj,
            brush=self.V_COLOR,
            pen=self.lines,
            size=self.SIZE,
            pxMode=self.PIXEL_MODE,
        )

        self.iteration -= 1

        if self.iteration == 0:
            self.prev_button.setEnabled(False)

        self.next_button.setEnabled(True)
        self.play_button.setEnabled(True)

        self.highlight_edge(self.iteration)
        # if self.iteration in self.graph.mst_indices:
        #     self.lines[self.iteration] = (0,0,255,255,1)

        # self.g.setData(
        #     pos=self.pos,
        #     adj=self.adj,
        #     brush=self.V_COLOR,
        #     pen=self.lines,
        #     size=self.SIZE,
        #     pxMode=self.PIXEL_MODE,
        # )

        # pg.QtGui.QApplication.processEvents()
        self.update_edge_list(direction=True)

        # Need to signal thread of changes to lines and iteration
        self.sig.emit((self.lines, self.iteration))

    def play(self):

        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.thread.is_running = True
        self.thread.start()
        self.thread.sig.connect(self.update_data)
        self.play_button.hide()
        self.pause_button.show()

    def update_data(self, payload):

        self.lines, self.iteration = payload[0], payload[1]
        self.g.setData(
            pos=self.pos,
            adj=self.adj,
            brush=self.V_COLOR,
            pen=self.lines,
            size=self.SIZE,
            pxMode=self.PIXEL_MODE,
        )
        pg.QtGui.QApplication.processEvents()
        self.update_edge_list(direction=False)

        if self.iteration == NUM_VERTICES - 2:
            self.pause_button.hide()
            self.play_button.show()
            self.play_button.setEnabled(False)
            self.prev_button.setEnabled(True)

    # direction: False = forward, True = backwards
    def update_edge_list(self, direction):

        if not direction:
            for i in range(len(self.edge_label_array)-1):
                self.edge_label_array[i].setText(self.edge_label_array[i+1].text())

            if len(self.lines)-self.iteration >= 5:
                u,v,w = self.graph.graph[self.iteration]
                new_string = str(u)+"\t"+str(v)+"\t"+str(w)
                self.edge_label_array[-1].setText(new_string)
            else:
                self.edge_label_array[-1].setText("")

    def pause(self):

        try:
            self.thread.is_running = False

            self.pause_button.hide()
            self.play_button.show()
            self.play_flag = False
            self.prev_button.setEnabled(True)

            if self.iteration < NUM_EDGES - 1:
                self.next_button.setEnabled(True)
        except:
            pass

    def fade_in(self):
        self.next_button.setEnabled(False)
        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(False)

        i = 5
        while i <= 255:
            self.g.setData(
                pos=self.pos,
                adj=self.adj,
                brush=(255, 255, 255, i),
                pen=self.lines,
                size=self.SIZE,
                pxMode=self.PIXEL_MODE,
            )
            pg.QtGui.QApplication.processEvents()
            i += 5
            time.sleep(0.05)

        i = 1
        while i <= 32:
            self.g.setData(
                pos=self.pos,
                adj=self.adj,
                brush=self.V_COLOR,
                pen=(255, 255, 255, i),
                size=self.SIZE,
                pxMode=self.PIXEL_MODE,
            )
            pg.QtGui.QApplication.processEvents()
            i += 1
            time.sleep(0.03)

        for i in range(len(self.lines)):
            self.lines[i] = (255, 255, 255, 32, 1)

        self.next_button.setEnabled(True)
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(True)

    def highlight_edge(self, edge):

        if edge >= NUM_EDGES:
            return
        self.lines[edge] = (0,0,255,255,1)
        self.g.setData(
            pos=self.pos,
            adj=self.adj,
            brush=self.V_COLOR,
            pen=self.lines,
            size=self.SIZE,
            pxMode=self.PIXEL_MODE,
        )
        pg.QtGui.QApplication.processEvents()

# Start Qt event loop unless running in interactive mode or using pyside.
def main():

    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec_()


if __name__ == "__main__":
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, "PYQT_VERSION"):
        main()
