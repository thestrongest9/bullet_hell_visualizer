import matplotlib.pyplot as plt
import time as TIME

class Graph:
    def __init__(self, title=None, x_label=None, y_label=None):
        plt.ion()
        self.fig, self.ax = plt.subplots()
        # self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 1)
        self.ax.xaxis.get_major_locator().set_params(integer=True)
        self.ylimit = 1

        self.weak_values = []
        self.strg_values = []
        self.turns = []

        # Add title and labels
        if title != None:
            self.ax.set_title(title)
        if x_label != None:
            self.ax.set_xlabel(x_label)
        if y_label != None:
            self.ax.set_ylabel(y_label)

        self.line_weak, = self.ax.plot([], [], label="Weak")
        self.line_strg, = self.ax.plot([], [], label="Strong")
        
        self.ax.legend(loc="lower left")

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def update(self, turn, weak_data, strg_data):
        weak_avg = sum(weak_data) / len(weak_data)
        strg_avg = sum(strg_data) / len(strg_data)

        if weak_avg > self.ylimit or strg_avg > self.ylimit:
            self.ylimit = strg_avg if strg_avg > weak_avg else weak_avg
            self.ax.set_ylim(0, self.ylimit)

        if self.turns == [] or self.turns[-1]+1 == turn:
            self.weak_values.append(weak_avg)
            self.strg_values.append(strg_avg)
            self.turns.append(turn)
            # self.turns = range(0, turn+1)
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