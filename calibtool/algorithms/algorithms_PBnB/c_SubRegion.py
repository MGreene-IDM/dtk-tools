# -*- coding: utf-8 -*-
"""
Created on Fri Jun 23 14:21:27 2017

@author: TingYu Ho
"""


class c_SubRegion(object): 
    def __init__(self, coordinate_lower, coordinate_upper, params):
        import pandas as pd  # this is how I usually import pandas
        import numpy as np
        self.s_label = 'C'  # C: undetermined, P:prune, M:maintain
        self.b_activate = True  # become false if branching into two
        self.b_branchable = True
        self.b_elite = False
        self.b_worst = False
        self.b_maintaining_indicator = False  # prepared to maintain in this time
        self.b_pruning_indicator = False  # prepared to prune in this time
        self.l_sample = []  # list of sampling points in this subregion
        self.l_coordinate_lower = coordinate_lower  # lower bound of this region
        self.l_coordinate_upper = coordinate_upper  # upper bound of this region
        self.array_distance = np.array(self.l_coordinate_upper)-np.array(self.l_coordinate_lower)
        self.f_volume = np.prod(self.array_distance[self.array_distance != 0])  # volume of the subregion
        #self.l_coordinate_sample = []
        #for l in l_para: #sample coordinate
            #self.l_coordinate_sample.append(l)
        self.i_min_sample = 0  # minimum value of sampling points in this subregions
        self.i_max_sample = 0  # maximum value of sampling points in this subregions
        self.f_min_diff_sample_mean = 0.  # minimum value of difference of sorted sampling points in this subregions
        self.f_max_var = 0.   # maximum value of variance of sampling points in this subregions
        #self.l_sample_dataset = []
        #self.pd_sample_record = pd.DataFrame([], columns=[])
        #for i in range(0, len(l_para)): # create the dataset record the sampling data corordinate in this subregion
            #self.pd_sample_record[self.l_coordinate_sample[i]] = pd.Series(float, index=self.pd_sample_record.index)
        #self.pd_sample_record['# rep'] = pd.Series(0, index=self.pd_sample_record.index) # number of replication
        #self.pd_sample_record['# rep'].astype(int)
        #self.pd_sample_record['mean'] = pd.Series(0, index=self.pd_sample_record.index)
        #self.pd_sample_record['var'] = pd.Series(0, index=self.pd_sample_record.index)
        #self.pd_sample_record['SST'] = pd.Series(0, index=self.pd_sample_record.index)
        #self.pd_sample_record['iteration'] = pd.Series(0, index=self.pd_sample_record.index)
        self.pd_sample_record = pd.DataFrame([], columns=[p['Name'] for p in params]+['# rep']+['mean']+['var']+['SST'])
        self.pd_sample_record['# rep'].astype(int)
        self.pd_sample_record['mean'].astype(int)
        self.pd_sample_record['var'].astype(float)
        self.pd_sample_record['SST'].astype(float)
