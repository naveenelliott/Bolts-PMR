import pandas as pd
import numpy as np
import os
import streamlit as st

def MeanAndStdDev(everything):
    locations = ['x', 'y', 'ex', 'ey']
    everything[locations] = everything[locations].astype(float)
    for index, row in everything.iterrows():
        if row['Dir'] == 'RL':
            everything.at[index, 'x'] = 120 - everything.at[index, 'x']
            everything.at[index, 'y'] = 80 - everything.at[index, 'y']
            everything.at[index, 'ex'] = 120 - everything.at[index, 'ex']
            everything.at[index, 'ey'] = 80 - everything.at[index, 'ey']
            

    need_different = ['Forward', 'Side Back', 'Dribble', 'Cross', 'Long', 'Ground GK', 'Throw']
    everything.dropna(subset=['x'], inplace=True)

    everything = everything.loc[everything['Action'].isin(need_different)]

    def filter_rows(row):
        action = row['Action']
        if action in need_different:
            if row['x'] == row['ex'] or row['y'] == row['ey']:
                return False  # Delete the row
        return True  # Keep the row

    # Apply the filter function to each row
    everything = everything[everything.apply(filter_rows, axis=1)].reset_index(drop=True)
    xT = np.array([[0.00638303, 0.00779616, 0.00844854, 0.00977659, 0.01126267,
            0.01248344, 0.01473596, 0.0174506 , 0.02122129, 0.02756312,
            0.03485072, 0.0379259 ],
        [0.00750072, 0.00878589, 0.00942382, 0.0105949 , 0.01214719,
            0.0138454 , 0.01611813, 0.01870347, 0.02401521, 0.02953272,
            0.04066992, 0.04647721],
        [0.0088799 , 0.00977745, 0.01001304, 0.01110462, 0.01269174,
            0.01429128, 0.01685596, 0.01935132, 0.0241224 , 0.02855202,
            0.05491138, 0.06442595],
        [0.00941056, 0.01082722, 0.01016549, 0.01132376, 0.01262646,
            0.01484598, 0.01689528, 0.0199707 , 0.02385149, 0.03511326,
            0.10805102, 0.25745362],
        [0.00941056, 0.01082722, 0.01016549, 0.01132376, 0.01262646,
            0.01484598, 0.01689528, 0.0199707 , 0.02385149, 0.03511326,
            0.10805102, 0.25745362],
        [0.0088799 , 0.00977745, 0.01001304, 0.01110462, 0.01269174,
            0.01429128, 0.01685596, 0.01935132, 0.0241224 , 0.02855202,
            0.05491138, 0.06442595],
        [0.00750072, 0.00878589, 0.00942382, 0.0105949 , 0.01214719,
            0.0138454 , 0.01611813, 0.01870347, 0.02401521, 0.02953272,
            0.04066992, 0.04647721],
        [0.00638303, 0.00779616, 0.00844854, 0.00977659, 0.01126267,
            0.01248344, 0.01473596, 0.0174506 , 0.02122129, 0.02756312,
            0.03485072, 0.0379259 ]])
    xT_rows, xT_cols = xT.shape
    np.random.seed(42)
    x = np.random.uniform(0, 120, 1000)
    y = np.random.uniform(0, 80, 1000)
    ex = np.random.uniform(0, 120, 1000)
    ey = np.random.uniform(0, 80, 1000)

    add_data = pd.DataFrame({'x': x, 
                        'y': y,
                        'ex': ex,
                        'ey': ey})
    x_bins = pd.cut(add_data['x'], xT_cols, retbins=True)[1]
    y_bins = pd.cut(add_data['y'], xT_rows, retbins=True)[1]
    ex_bins = pd.cut(add_data['ex'], xT_cols, retbins=True)[1]
    ey_bins = pd.cut(add_data['ey'], xT_rows, retbins=True)[1]

    everything['x1_bin'] = pd.cut(everything['x'], bins=x_bins, labels=False, include_lowest=True)
    everything['y1_bin'] = pd.cut(everything['y'], bins=y_bins, labels=False, include_lowest=True)
    everything['x2_bin'] = pd.cut(everything['ex'], bins=ex_bins, labels=False, include_lowest=True)
    everything['y2_bin'] = pd.cut(everything['ey'], bins=ey_bins, labels=False, include_lowest=True)

    everything.dropna(subset=['x1_bin', 'y1_bin', 'x2_bin', 'y2_bin'], inplace=True)
    everything.reset_index(drop=True)
    everything['y1_bin'] = everything['y1_bin'].astype(int)
    everything['y2_bin'] = everything['y2_bin'].astype(int)
    everything['x1_bin'] = everything['x1_bin'].astype(int)
    everything['x2_bin'] = everything['x2_bin'].astype(int)


    everything['start_zone_value'] = everything[['x1_bin', 'y1_bin']].apply(lambda x: xT[x[1], x[0]], axis=1)
    everything['end_zone_value'] = everything[['x2_bin', 'y2_bin']].apply(lambda x: xT[x[1], x[0]], axis=1)

    everything['xT'] = everything['end_zone_value'] - everything['start_zone_value']

    all = everything.groupby(['Team', 'Opposition'])['xT'].sum()
    all = all.to_frame()
    all.reset_index(inplace=True)
    del all['Opposition']
    for index, row in all.iterrows():
        if 'U13' in row['Team']:
            all.at[index, 'xT'] = (row['xT'] / 70) * 90
        elif 'U14' in row['Team'] or 'U15' in row['Team']:
            all.at[index, 'xT'] = (row['xT'] / 80) * 90

    mean_all = all['xT'].mean()
    std_all = all['xT'].std()
    return mean_all, std_all
