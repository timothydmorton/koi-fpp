#!/usr/bin/env python

import numpy as np
import pandas as pd

app_hammerfile = 'forTim_kplr20151218020451_appham.txt'

d = {}
for line in open(app_hammerfile):
    line = line.strip().split('|')
    try:
        if line[1] not in d:
            d[line[1]] = {}
        if line[3] == 'NULL':
            val = np.nan
        else:
            try:
                val = float(line[3])
            except ValueError:
                val = line[3]
        d[line[1]][line[2]] = val
    except:
        raise
        print('error with line: {}'.format(line))
        
df = pd.DataFrame.from_dict(d, orient='index')
df.to_csv('positional_probability.csv')
