import matplotlib.pyplot as plt
import time as TIME

class Graph:
    def __init__(self):
        plt.ion()
        self.fig, self.ax = plt.subplots()
        # self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 1)

        self.weak_values = []
        self.strg_values = []
        self.turns = []

        self.line_weak, = self.ax.plot([], [])
        self.line_strg, = self.ax.plot([], [])
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def update(self, turn, weak_data, strg_data):
        weak_avg = sum(weak_data) / len(weak_data)
        strg_avg = sum(strg_data) / len(strg_data)

        if self.turns == [] or self.turns[-1]+1 == turn:
            self.weak_values.append(weak_avg)
            self.strg_values.append(strg_avg)
            self.turns.append(turn)
            self.ax.set_xlim(0, turn)
        else:
            self.weak_values[turn] = weak_avg
            self.strg_values[turn] = strg_avg

        self.line_weak.set_data(self.turns, self.weak_values)
        self.line_strg.set_data(self.turns, self.strg_values)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        # plt.ioff()
        plt.show()

    def display(self):
        plt.ioff()
        plt.show()