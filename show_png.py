# -*- coding: utf-8 -*-
"""
Created on Mon Aug 13 13:33:54 2018

@author: CLUO17
"""

#%% load packages
import pandas as pd 
import tqdm
import numpy as np 
import matplotlib.pyplot as plt

#%% 
@pd.api.extensions.register_dataframe_accessor("descriptor")
class myDataFrame(pd.DataFrame):
    def __init__(self, data):
        self._data = data
    
    def col_description(self, col_name):
        
        # count # distinct
        not_null = self._data[col_name].loc[self._data[col_name].notnull()]
        n_distinct = len(set(not_null))
        
        # count # null
        n_null = sum(self._data[col_name].isnull())
        
        # count freq of each distinct value
        if n_null == self._data.shape[0]:
            value_counts = pd.DataFrame({'NULL':[n_null]}, index = ['NULL'])
        else:
            value_counts = self._data[col_name].value_counts()
            value_counts = value_counts / len(self._data[col_name])
              
        # only print 10 distinct value distributions
        if n_distinct > 10:
            value_counts_max = value_counts.iloc[:5]
            value_counts_min = value_counts.iloc[-5:]
            value_counts = pd.concat([value_counts_max, value_counts_min])
            
        # set index to at most 10 characters
        value_counts.index = [str(x)[:6] for x in value_counts.index]
        
        return col_name, n_distinct, n_null, value_counts
    
    def summary(self):
        return self._data.shape
    
    def description(self):
        result = list()
        for col in tqdm.tqdm(self._data.columns):
            result.append(self.col_description(col))
        return result

#%% define texts
def figure_title(df_shape):
    header = "Overview of the data\n"
    text = "Number of Rows: %d\nNumber of Columns: %d\n" %(df_shape[0], df_shape[1])
    if df_shape[0] > 10000:
        remark = "REMARK: Based on a sample of size 10000"
        text += remark
    return header + text
    
def sub_figure_title(description):
    text = str(description[0]) + "\n"
    text += "# DISTINCT: %d\n" % description[1]
    text += "# NULL: %d" % description[2]
    return text

#%% deploy
def display(df, dest_name):
    nrows = int(np.ceil(df.shape[1] / 3))
    fig, axs = plt.subplots(nrows = nrows,
                            ncols = 3,
                            figsize = (20, nrows * 6))
    axs = axs.ravel()
    
    # configuration of the whole
    header_text = figure_title(df.shape)
    fig.suptitle(header_text)
    fig.subplots_adjust(hspace = 0.5)
    
    # sample a fraction of the df so computer faster
    if df.shape[0] > 10000:
        idx = np.random.permutation(df.shape[0])
        df = df.iloc[idx[:10000]]
    
    # show column descriptions
    i = 0
    for col_name in tqdm.tqdm(df.columns):
        
        description = df.descriptor.col_description(col_name)
        sub_header_text = sub_figure_title(description)
        description[3].plot(kind = 'bar', 
                             ax = axs[i], 
                             rot = 45)
        axs[i].set_title(sub_header_text)

        i+= 1
    
    fig.savefig(dest_name + '.png')
    