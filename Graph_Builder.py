# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 20:53:36 2018

@author: AS39240
"""
import tkinter as tk

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def _edit(event):
    print(event.char)


class DataHandler(object):

    def __init__(self, obj):

        self.obj = obj
        self.type = self.dtype(self.obj)

    def _dict_list(self):

        data = (list(self.obj.keys()), list(self.obj.values()))
        return data

    def _df_list(self):

        if isinstance(self.obj, pd.Series):
            data = (self.obj.name, list(self.obj))
        elif isinstance(self.obj, pd.DataFrame):
            data = self.obj.to_dict()
            data = self._dict_list(data)
        return data

    def _arr_list(self):

        data = list(self.obj)
        return data

    def dtype(self, obj=None):

        if isinstance(obj, np.ndarray):
            _type = 'numpy'
        elif isinstance(obj, pd.DataFrame) or isinstance(obj, pd.Series):
            _type = 'pandas'
        elif isinstance(obj, dict):
            _type = 'dict'

        return _type

    def to_list(self):

        _to_list = {'numpy': self._arr_list, 'dict': self._dict_list,
                    'pandas': self._df_list}

        _klass = _to_list[self.type]

        return _klass()


class _Graph(object):
    _kinds = ['line', 'scatter', 'bar', 'box']

    def __init__(self, root=None, **kwds):

        self.root = root
        self.frame = tk.Frame(master=self.root, relief=tk.RAISED)

        self.fig = plt.figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.curr_kinds = []

        self.draw_graph(ax=self.ax)

    def draw_graph(self, ax=None, df=None):

        if ax is None:
            ax = self.ax

        ax.clear()

        orig_df = df

        for item in self.curr_kinds:
            if item == 'scatter':
                cols = list(orig_df.columns)
                for col in cols:
                    print(col)
                    ax.scatter(orig_df.index, orig_df[col])
            else:
                print("Orig Df")
                print(orig_df)
                orig_df.plot(kind=item, ax=ax)

        self.canvas.draw()

    def _grid(self, row, column):

        self.frame.grid(row=row, column=column)

    def graph_test(self):

        pass


class _ColBox(object):

    def __init__(self, root, df):

        self.root = root
        self.df = df
        self.current = None

        self.frame = tk.Frame(master=self.root, relief=tk.RAISED)
        self.col_box = tk.Listbox(master=self.frame, selectmode=tk.EXTENDED)
        self.col_box.pack()

        self.col_box.insert(tk.END, 'Index')

        for itm in self.df:
            self.col_box.insert(tk.END, itm)

        self.poll()

    def _grid(self, row, column):

        self.frame.grid(row=row, column=column)

    def poll(self):

        now = self.col_box.curselection()
        now = [self.col_box.get(i) for i in now]
        if now != self.current:
            self.current = now
        self.col_box.after(250, self.poll)


class _Label(object):

    def __init__(self, root=None, label=None, **kwds):

        _pop_attr = ['orient', 'r_mouse', 'l_mouse', 'double_click']
        _def_attr = {'orient': 'Verticle', 'r_mouse': self._r_mouse,
                     'l_mouse': self._l_mouse, 'double_click': self._double_click}

        for attr in _pop_attr:
            value = kwds.pop(attr, _def_attr.get(attr, None))
            setattr(self, attr, value)

        self.root = root
        self.org_lable = label

        if self.orient == 'Verticle':
            self.label = "\n".join(label)
        else:
            self.label = label

        self.labelframe = tk.LabelFrame(master=self.root)
        self.orig_color = self.labelframe.cget("background")

        self.text = tk.Label(self.labelframe, text=self.label)

        self.text.bind('<Button-1>', self.r_mouse)
        self.text.bind('<Button-3>', self.l_mouse)
        self.text.pack()

    def _r_mouse(self, event):
        event.widget.config(bg='light blue')
        event.widget.focus_set()
        event.widget.bind('<Key>', self.edit)

    def _l_mouse(self, event):
        event.widget.config(bg=self.orig_color)
        event.widget.focus_set()
        event.widget.bind('<Key>', self.edit)

    def _double_click(self, event):
        pass

    def _grid(self, row, column):

        self.labelframe.grid(row=row, column=column)


class _Checkbar(tk.Frame):

    def __init__(self, parent=None, picks=None, command=None,
                 side=tk.LEFT, anchor=tk.W):
        tk.Frame.__init__(self, parent)
        self.vars = []
        self.chks = []
        for i, pick in enumerate(picks):
            var = tk.IntVar()
            chk = tk.Checkbutton(self, text=pick, variable=var,
                                 indicatoron=0, command=command)
            chk.pack(side=side, anchor=anchor, expand=tk.YES)
            self.vars.append(var)
            self.chks.append(var)

    def get_state(self):
        return list(map(lambda var: var.get(), self.vars))

    def _grid(self, row, column):

        self.grid(row=row, column=column)


class GraphBuilder(object):

    def __init__(self, df):

        self.y_text = ''
        self.x_text = ''

        self.df = df

        self.graph_df = pd.DataFrame()

        self.master = tk.Tk()

        self.col_box = _ColBox(root=self.master, df=self.df)
        self.col_box._grid(row=1, column=0)

        self.graph = _Graph(root=self.master)
        self.graph._grid(row=1, column=2)

        self.graph_lst = ['Scatter', 'Line', 'Bar', 'Box Whisker']

        self.check_bar = _Checkbar(parent=self.master, picks=self.graph_lst, command=self.change_graph)
        self.check_bar._grid(row=0, column=2)

        self.y_label = _Label(root=self.master, label="Drag y|variable here",
                              orient='Verticle', r_mouse=self.add_ycol,
                              l_mouse=self.del_ycol)
        self.y_label._grid(row=1, column=1)

        self.x_label = _Label(root=self.master, label="Drag x-variable here",
                              orient='Horizontal', r_mouse=self.set_xcol,
                              l_mouse=self.reset_xcol)

        self.x_label._grid(row=2, column=2)

        self.xcol = None
        self.ycols = []

        # Let Tk take over
        tk.mainloop()

    def change_graph(self):

        _attr_list = ['scatter', 'line', 'bar', 'box']

        states = self.check_bar.get_state()
        #print(states)
        self.graph.curr_kinds = []
        for i, item in enumerate(states):
            if item == 1:
                self.graph.curr_kinds.append(_attr_list[i])

        self.create_graph_df()
        #print(self.graph_df)
        self.graph.draw_graph(ax=self.graph.ax, df=self.graph_df)

    def create_graph_df(self):

        col_dict = {}
        self.graph_df = pd.DataFrame()

        for name in self.ycols:
            col_dict[name] = self.df[name]

        print(self.xcol)
        print(self.ycols)
        if self.xcol is None:
            index_vals = self.df.index
        else:
            #print(self.xcol)
            index_vals = self.df[self.xcol]

        col_dict['Index'] = index_vals

        self.graph_df = pd.DataFrame(data=col_dict)
        self.graph_df.set_index('Index', inplace=True)
        try:
            self.graph_df.drop(columns='Index', axis=1, inplace=True)
        except KeyError:
            pass
        print(self.graph_df)

    def set_xcol(self, event):
        event.widget.config(bg='light blue')
        event.widget.focus_set()
        event.widget.bind('<Key>', _edit)
        self.xcol = self.col_box.current[0]
        self.create_graph_df()
        self.graph.draw_graph(ax=self.graph.ax, df=self.graph_df)
        self.x_text = self.xcol
        event.widget.config(text=self.x_text)

    def reset_xcol(self, event):
        event.widget.config(bg=self.x_label.orig_color)
        event.widget.focus_set()
        event.widget.bind('<Key>', _edit)
        self.xcol = None
        self.graph.cur_x = []
        self.graph.draw_graph(ax=self.graph.ax, df=self.graph_df)
        event.widget.config(text="Drag x-variable here")

    def add_ycol(self, event):
        event.widget.config(bg='light blue')
        event.widget.focus_set()
        event.widget.bind('<Key>', _edit)
        for itm in self.col_box.current:
            self.ycols.append(itm)
        #print(self.ycols)
        self.create_graph_df()
        self.graph.draw_graph(ax=self.graph.ax, df=self.graph_df)
        self.y_text = ''
        for i, col in enumerate(self.ycols):
            if i == len(self.ycols)-1:
                self.y_text += ' '+col
            elif i == 0:
                self.y_text += col
            else:
                self.y_text += ' '+col+','

        self.y_text = "\n".join(self.y_text)
        event.widget.config(text=self.y_text)

    def del_ycol(self, event):
        event.widget.config(bg=self.y_label.orig_color)
        event.widget.focus_set()
        event.widget.bind('<Key>', _edit)
        self.ycol = None
        self.graph.cur_y = []
        # self.graph.draw_graph(fig = self.graph.fig, ax = self.graph.ax)
        self.y_text = "Drag y-variable here"
        self.y_text = "\n".join(self.y_text)
        event.widget.config(text=self.y_text)


test_x = np.linspace(0, 100, 100)
test_y = 2.0 * np.sin(1.25 * test_x + 0.5) + 1
test_x = list(test_x)
test_y = list(test_y)
test_df = pd.DataFrame({"X": test_x, "Y": test_y})
#test_df = pd.DataFraem({"Label":['Apple', 'Orange', 'Kiwi']})
obj = GraphBuilder(test_df)
