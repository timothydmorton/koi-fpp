
import numpy as np
import pandas as pd

d = {}

for line in open('probability_table_hammer.txt'):
    line = line.split('|')
    try:
        line[3] = line[3].strip()
        if line[1] not in d:
            d[line[1]] = {}
        if line[3]=='NULL':
            val = np.nan
        else:
            try:
                val = float(line[3])
            except ValueError:
                val = line[3]
        d[line[1]][line[2]] = val
    except:
        print('error with {}'.format(line))
        
df = pd.DataFrame.from_dict(d, orient='index')

df.to_csv('positional_probability.csv')