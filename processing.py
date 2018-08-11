# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 10:22:13 2018

@author: CLUO17
"""

#%% IMPORT PACKAGE
import pandas as pd 
from matplotlib.figure import Figure
from tkinter import *
from collections import defaultdict
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import tqdm
import numpy as np 

#%% 
@pd.api.extensions.register_dataframe_accessor("descriptor")
class myDataFrame(pd.DataFrame):
    def __init__(self, data):
        self._data = data
    
    def col_description(self, col_name):
        
        # count three important values
        n_distinct = len(set(self._data[col_name]))
        n_null = sum(self._data[col_name].isnull())
        value_counts = self._data[col_name].value_counts()
        value_counts = value_counts / (len(self._data[col_name]) - n_null)
              
        # only print 10 distinct value distributions
        if n_distinct > 10:
            value_counts_max = value_counts.iloc[:5]
            value_counts_min = value_counts.iloc[-5:]
            value_counts = pd.concat([value_counts_max, value_counts_min])
        
        # print NULL distribution
        if n_null > 0:
            value_counts = value_counts.append(pd.Series([n_null / self._data.shape[0]], 
                                                         index = ['NULL']))
        
        return col_name, n_distinct, n_null, value_counts
    
    def summary(self):
        return self._data.shape
    
    def description(self):
        result = list()
        for col in tqdm.tqdm(self._data.columns):
            result.append(self.col_description(col))
        return result

#%%
def printDescription(description):
    text = "%s\n# DISTINCT: %d\n# NULL: %d" \
           %(description[0], description[1], description[2])
    return text

def onFrameConfigure(canvas):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))

#%%     
def display(df):
    root = Tk()
    root.title("Data Description")
    
    # overview of the table
    text = "Number of rows: %d \n Nuber of columns: %d" %(df.shape[0], df.shape[1])
    lbl = Label(root, text = text, bg = "white", fg = "red") 
    lbl.pack(side = 'top')
    
    # sample a fraction of the df so computer faster
    if df.shape[0] > 10000:
        idx = np.random.permutation(df.shape[0])
        df = df.iloc[idx[:10000]]
    
    # canvas
    canvas = Canvas(root, bg = 'grey', width = 1500)
    canvas.pack(side = 'left', fill = 'y', expand = True)
    
    # scrollbar
    vbar = Scrollbar(root, orient = 'vertical', command = canvas.yview)
    vbar.pack(side = 'right', fill = 'y')
    
    # window
    frame = Frame(canvas, bg = 'white', width = 2000)
    frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))
    canvas.create_window((0,0), window = frame, anchor = 'nw')
    
    # each column of df
    labels = defaultdict(Label)
    figures = defaultdict(Figure)
    i = 0
    j = 1
    for col in tqdm.tqdm(df.columns):
        description = df.descriptor.col_description(col)
        
        # text
        labels[col] = Label(frame,
                            text = printDescription(description),
                            bg = "white")
        labels[col].grid(column = i, row = j)
        
        # plot figure
        figures[col] = Figure(figsize = (6,6))
        ax = figures[col].add_subplot(111)
        description[-1].plot(kind = 'bar', 
                             ax = ax, 
                             rot = 45,
                             figsize = (6,6))
        
        # show figure
        canvas = FigureCanvasTkAgg(figures[col], frame)
        canvas.show()
        canvas.get_tk_widget().grid(column = i, row = j+1)
        
        # compute column of the window
        i += 1
        i %= 3
        
        # compute row of the window
        if i == 0:
            j += 2
    
    root.mainloop()         