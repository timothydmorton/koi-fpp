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
positional_file = 'target_probabilities_high_confidence_02-Jan-2014.txt'
starprop_file = 'starprops_all.txt'

fpp_table = pd.read_table(fpp_file, delim_whitespace=True)
fpp_table.index = fpp_table['koi']

positional_table = pd.read_table(positional_file, delim_whitespace=True)
positional_table.index = positional_table['koi'].apply(ku.koiname)

star_table = pd.read_table(starprop_file, delim_whitespace=True)
star_table.index = star_table['koi']

kois = fpp_table.index

fpp_table['rp'] = fpp_table.ix[kois, 'rprs'] * star_table.ix[kois, 'radius'] * RSUN/REARTH
fpp_table['disposition'] = ku.DATA.ix[kois, 'koi_disposition']
fpp_table['prob_ontarget'] = positional_table.ix[kois, 'prob_target']
fpp_table['not_transitlike'] = ku.DATA.ix[kois, 'koi_fpflag_nt'].astype(bool)
fpp_table['signficant_secondary'] = ku.DATA.ix[kois, 'koi_fpflag_ss'].astype(bool)
fpp_table['centroid_offset'] = ku.DATA.ix[kois, 'koi_fpflag_co'].astype(bool)
fpp_table['ephem_match'] = ku.DATA.ix[kois, 'koi_fpflag_ec'].astype(bool)


secdepth = np.zeros(len(kois))
r_excl = np.zeros(len(kois))
for i,koi in enumerate(fpp_table.index):
    try:
        config = ConfigObj(os.path.join(FPPDIR, ku.koiname(koi), 'fpp.ini'))
        secdepth[i] = float(config['constraints']['secthresh'])*1e6
        r_excl[i] = float(config['constraints']['maxrad'])
    except KeyboardInterrupt:
        raise
    except:
        secdepth[i] = np.nan
        r_excl[i] = np.nan

fpp_table['secdepth'] = secdepth
fpp_table['r_excl'] = r_excl

fpp_table.to_csv('fpp_final_table.csv')

    
