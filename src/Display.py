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

NUM_VERTICES = 15
# Must be at least NUM_VERTICES - 1
NUM_EDGES = 0


class Window(QMainWindow):
    def __init__(self):

        super(Window, self).__init__()
        self.setGeometry(50, 50, 1024, 760)
        self.setWindowTitle("ALgorithm Visualizations")
        self.setWindowIcon(QtGui.QIcon("meta/treelogo.png"))

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.black)
        self.setPalette(p)

        # self.initialize_layouts()
        self.central_widget = QtGui.QStackedWidget()
        self.setCentralWidget(self.central_widget)
        home_widget = HomeWidget(self)
        self.central_widget.addWidget(home_widget)

    def start(self):

        animation_widget = AnimationWidget(self)

        # setup buttons
        # self.b1.hide()

        self.central_widget.addWidget(animation_widget)
        self.central_widget.setCurrentIndex(1)
        self.central_widget.currentWidget().launch()

    def return_home(self):

        self.central_widget.setCurrentIndex(0)


class HomeWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(HomeWidget, self).__init__(parent)
        layout = QtGui.QHBoxLayout()
        kruskal_button = QPushButton("Kruskal")
        kruskal_button.clicked.connect(self.parent().start)
        layout.addWidget(kruskal_button)
        prim_button = QPushButton("Prim")
        layout.addWidget(prim_button)
        self.setLayout(layout)


class AnimationWidget(QtGui.QWidget):

    sig = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super(AnimationWidget, self).__init__(parent)
        self.lines = []
        self.pos = []
        self.adj = []
        self.g = ""
        self.PIXEL_MODE = True
        self.SIZE = 10
        self.graph = Graph.Graph(NUM_VERTICES, NUM_EDGES)

        # UI Colors
        self.MST_EDGE_COLOR = (255, 191, 0, 255, 1)
        self.DEFAULT_EDGE_COLOR = (255, 255, 255, 32, 1)

        self.init_layout()

    def launch(self):

        self.reset()

        # animations
        self.fade_in()
        self.highlight_edge(self.iteration)
        # Labels
        # TODO: Add animation for labels
        self.edge_table_label.show()
        for i in range(len(self.edge_label_array)):
            self.edge_label_array[i].show()

        self.home_button.setEnabled(True)

    def reset(self):

        self.edge_table_label.hide()
        # for i in range(len(self.edge_label_array)):
        #     self.edge_label_array[i].hide()

        for item in enumerate(self.edge_label_array):
            ind, label = item

            edge = self.graph.graph[ind]
            label_str = label_str = (
                str(edge[0]) + "\t" + str(edge[1]) + "\t" + str(edge[2])
            )
            label.setText(label_str)
            if ind == 0:
                label.setStyleSheet(
                    "QLabel#tmp {color: white; background-color: rgba(255,255,255,20);}"
                )
            else:
                label.setStyleSheet("QLabel#tmp {color: white}")
            label.hide()

        self.iteration = 0
        for item in enumerate(self.lines):
            self.lines[item[0]] = (255, 255, 255, 0, 1)

        self.g.setData(
            pos=self.pos,
            adj=self.adj,
            brush=(0, 0, 0, 0),
            pen=self.lines,
            size=self.SIZE,
            pxMode=self.PIXEL_MODE,
        )
        pg.QtGui.QApplication.processEvents()

        # self.update_edge_list(False)

    def init_layout(self):

        animation_layout = QVBoxLayout()

        self.home_button = QtGui.QPushButton()
        self.home_button.setIcon(QtGui.QIcon("meta/homebutton.png"))
        self.home_button.clicked.connect(self.parent().return_home)
        self.home_button.setEnabled(False)
        animation_layout.addWidget(self.home_button, alignment=QtCore.Qt.AlignLeft)

        graph_layout = QHBoxLayout()
        graph_layout.addWidget(self.init_graph())

        self.edge_table = QVBoxLayout()

        self.edge_table_label = QLabel("V 1\tV 2\tCost")
        self.edge_table_label.setObjectName("edge_table_label")
        self.edge_table_label.setStyleSheet("QLabel#edge_table_label {color: white}")
        self.edge_table_label.hide()
        self.edge_table.addWidget(self.edge_table_label)

        self.edge_label_array = []

        for i in range(5):
            edge = self.graph.graph[i]
            label_str = str(edge[0]) + "\t" + str(edge[1]) + "\t" + str(edge[2])
            tmp = QLabel(label_str)
            tmp.setObjectName("tmp")
            if i == 0:
                tmp.setStyleSheet(
                    "QLabel#tmp {color: white; background-color: rgba(255,255,255,20);}"
                )
            else:
                tmp.setStyleSheet("QLabel#tmp {color: white}")
            tmp.hide()
            self.edge_label_array.append(tmp)
            self.edge_table.addWidget(tmp)

        graph_layout.addLayout(self.edge_table)

        # self.b2 = QPushButton("Begin")
        # layout.addWidget(self.home())
        animation_layout.addLayout(graph_layout)

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
        animation_layout.addLayout(self.button_array)

        # b1 = QPushButton("Start")
        # b1.clicked.connect(start)
        # animation_layout.addWidget(b1)
        self.setLayout(animation_layout)

    def init_graph(self):

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

    # direction: False = forward, True = backwards
    def update_edge_list(self, direction):

        if not direction:
            for i in range(len(self.edge_label_array) - 1):
                self.edge_label_array[i].setText(self.edge_label_array[i + 1].text())

            if len(self.lines) - self.iteration > 4:
                u, v, w = self.graph.graph[self.iteration + 4]
                new_string = str(u) + "\t" + str(v) + "\t" + str(w)
                self.edge_label_array[-1].setText(new_string)
            else:
                self.edge_label_array[-1].setText("")

        # TODO: Breaking when at end of demonstration
        if direction:
            for i in reversed(range(1, len(self.edge_label_array))):
                self.edge_label_array[i].setText(self.edge_label_array[i - 1].text())

            u, v, w = self.graph.graph[self.iteration]
            new_string = str(u) + "\t" + str(v) + "\t" + str(w)
            self.edge_label_array[0].setText(new_string)

    def init_play_thread(self):

        self.thread = Worker.Worker(NUM_VERTICES, self.lines, self.graph)
        self.sig.connect(self.thread.on_source)
        self.sig.emit((self.lines, self.iteration))
        self.thread.is_running = False

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
        self.highlight_edge(self.iteration)

        if self.iteration == len(self.lines):
            self.pause_button.hide()
            self.play_button.show()
            self.play_button.setEnabled(False)
            self.prev_button.setEnabled(True)

    def stop_thread():

        self.worker.stop()
        self.thread.quit()
        self.thread.wait()

    def next(self):

        if self.iteration == NUM_EDGES - 1:
            self.next_button.setEnabled(False)
            self.play_button.setEnabled(False)

        self.prev_button.setEnabled(True)

        if self.iteration in self.graph.mst_indices:
            self.lines[self.iteration] = self.MST_EDGE_COLOR
        else:
            self.lines[self.iteration] = self.DEFAULT_EDGE_COLOR

        self.g.setData(
            pos=self.pos,
            adj=self.adj,
            brush=self.V_COLOR,
            pen=self.lines,
            size=self.SIZE,
            pxMode=self.PIXEL_MODE,
        )
        # pg.QtGui.QApplication.processEvents()
        self.iteration += 1
        self.update_edge_list(direction=False)
        self.highlight_edge(self.iteration)

        # TODO: May not need this anymore
        # Need to signal thread of changes to lines and iteration
        self.sig.emit((self.lines, self.iteration))

    def prev(self):

        if self.iteration <= NUM_EDGES - 1:
            self.lines[self.iteration] = self.DEFAULT_EDGE_COLOR

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

        # pg.QtGui.QApplication.processEvents()
        self.update_edge_list(direction=True)

        # TODO: May not need this anymore
        # Need to signal thread of changes to lines and iteration
        self.sig.emit((self.lines, self.iteration))

    def play(self):

        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.init_play_thread()
        self.thread.is_running = True
        self.thread.start()
        self.thread.sig.connect(self.update_data)
        self.play_button.hide()
        self.pause_button.show()

    def pause(self):

        try:
            self.thread.is_running = False

            self.pause_button.hide()
            self.play_button.show()
            self.play_flag = False
            self.prev_button.setEnabled(True)

            if self.iteration < NUM_EDGES - 1:
                self.next_button.setEnabled(True)

            self.stop_thread()
        except:
            pass

    def fade_in(self):
        self.next_button.setEnabled(False)
        self.play_button.setEnabled(False)
        self.prev_button.setEnabled(False)

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
            i += 2
            time.sleep(0.03)

        for i in range(len(self.lines)):
            self.lines[i] = (255, 255, 255, 32, 1)

        self.next_button.setEnabled(True)
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(True)

    def highlight_edge(self, edge):

        if edge >= NUM_EDGES:
            return
        self.lines[edge] = (0, 255, 255, 255, 1)  # (0,0,255,255,1)
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
