#!/usr/bin/env python

import pandas as pd
import numpy as np
import os

from configobj import ConfigObj

from keputils import koiutils as ku

from astropy import constants as const
RSUN = const.R_sun.cgs.value
REARTH = const.R_earth.cgs.value

fpp_file = 'fpp_all.txt'
positional_file = 'positional_probability.csv'
starprop_file = 'starprops_all.txt'

fpp_table = pd.read_table(fpp_file, delim_whitespace=True)
fpp_table.index = fpp_table['koi']

positional_table = pd.read_csv(positional_file, index_col=0)

star_table = pd.read_table(starprop_file, delim_whitespace=True)
star_table.index = star_table['koi']

err_table = np.loadtxt('fpp_err.txt', usecols=(0,1), dtype=str)

kois = fpp_table.index

fpp_table['rp'] = fpp_table.ix[kois, 'rprs'] * star_table.ix[kois, 'radius'] * RSUN/REARTH
fpp_table['disposition'] = ku.DATA.ix[kois, 'koi_disposition']
fpp_table['prob_ontarget'] = positional_table.ix[kois, 'pp_host_rel_prob']
fpp_table['pos_prob_score'] = positional_table.ix[kois, 'pp_host_prob_score']
fpp_table['not_transitlike'] = ku.DATA.ix[kois, 'koi_fpflag_nt'].astype(bool)
fpp_table['significant_secondary'] = ku.DATA.ix[kois, 'koi_fpflag_ss'].astype(bool)
fpp_table['centroid_offset'] = ku.DATA.ix[kois, 'koi_fpflag_co'].astype(bool)
fpp_table['ephem_match'] = ku.DATA.ix[kois, 'koi_fpflag_ec'].astype(bool)

fpp_table['exception'] = None
fpp_table.ix[err_table[:,0], 'exception'] = err_table[:,1]
fpp_table['exception'] = fpp_table['exception'].str.replace(':','')

fpp_table.to_csv('fpp_final_table.csv')

    
