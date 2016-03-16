#!/usr/bin/env python

import pandas as pd
import numpy as np
import os

from keputils import koiutils as ku
DATA = ku.DR24

from astropy import constants as const
RSUN = const.R_sun.cgs.value
REARTH = const.R_earth.cgs.value

folder = 'data'

fpp_file = os.path.join(folder, 'fpp_all.txt')
positional_file = os.path.join(folder, 'positional_probability.csv')
starprop_file = os.path.join(folder, 'starprops_all.txt')

fpp_table = pd.read_table(fpp_file, delim_whitespace=True)
fpp_table.index = fpp_table['koi']

positional_table = pd.read_csv(positional_file, index_col=0)

star_table = pd.read_table(starprop_file, delim_whitespace=True)
star_table.index = star_table['koi']

ttv_file = os.path.join(folder, 'ttvdata.txt')
ttv_table = pd.read_table(ttv_file, index_col=0, delim_whitespace=True) 

err_file = os.path.join(folder, 'fpp_err.txt')
err_table = np.loadtxt(err_file, usecols=(0,1), dtype=str)


kois = fpp_table.index

fpp_table['kepid'] = DATA.ix[kois, 'kepid']
fpp_table['period'] = DATA.ix[kois, 'koi_period']
fpp_table['rp'] = fpp_table.ix[kois, 'rprs'] * star_table.ix[kois, 'radius'] * RSUN/REARTH
fpp_table['disposition'] = DATA.ix[kois, 'koi_disposition']
fpp_table['prob_ontarget'] = positional_table.ix[kois, 'pp_host_rel_prob']
fpp_table['pos_prob_score'] = positional_table.ix[kois, 'pp_host_prob_score']
fpp_table['not_transitlike'] = DATA.ix[kois, 'koi_fpflag_nt'].astype(bool)
fpp_table['significant_secondary'] = DATA.ix[kois, 'koi_fpflag_ss'].astype(bool)
fpp_table['centroid_offset'] = DATA.ix[kois, 'koi_fpflag_co'].astype(bool)
fpp_table['ephem_match'] = DATA.ix[kois, 'koi_fpflag_ec'].astype(bool)
fpp_table['MES'] = DATA.ix[kois, 'koi_max_mult_ev']

fpp_table['exception'] = None
fpp_table.ix[err_table[:,0], 'exception'] = err_table[:,1]
fpp_table['exception'] = fpp_table['exception'].str.replace(':','')

fpp_table['has_ttv'] = ttv_table.ix[kois,'has_ttv']
fpp_table['MES'] = DATA.ix[kois, 'koi_max_mult_ev']
fpp_table['n_cands'] = DATA.ix[kois, 'koi_count']


# Replace with mean values

fpp_mean = pd.read_csv('data/fpp_bootstrap_mean.csv')
fpp_mean.rename(columns={'Unnamed: 0':'koi'}, inplace=True)
fpp_mean.index = fpp_mean['koi']

fpp_max = pd.read_csv('data/fpp_bootstrap_max.csv')
fpp_max.rename(columns={'Unnamed: 0':'koi'}, inplace=True)
fpp_max.index = fpp_max['koi']

fpp_std = pd.read_csv('data/fpp_bootstrap_std.csv')
fpp_std.rename(columns={'Unnamed: 0':'koi'}, inplace=True)
fpp_std.index = fpp_std['koi']


for m in ['heb', 'eb', 'beb', 'heb', 'eb_Px2', 'beb_Px2', 'heb_Px2', 'long', 'boxy', 'pl']:
    for col in ['lhood_{}'.format(m), 'pr_{}'.format(m)]:
        fpp_table[col] = fpp_mean.ix[fpp_table.index, col]
        
fpp_table['FPP'] = fpp_mean.ix[fpp_table.index, 'FPP']
fpp_table['FPP_max'] = fpp_max.ix[fpp_table.index, 'FPP']
fpp_table['FPP_std'] = fpp_std.ix[fpp_table.index, 'FPP']


fpp_table.to_csv('fpp_final_table.csv')

    
