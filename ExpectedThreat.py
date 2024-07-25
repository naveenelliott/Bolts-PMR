import pandas as pd
import numpy as np
import os
import streamlit as st

def FindingExpectedThreat(total_events):
    locations = ['x', 'y', 'ex', 'ey']
    total_events[locations] = total_events[locations].astype(float)
    for index, row in total_events.iterrows():
        if row['Dir'] == 'RL':
            total_events.at[index, 'x'] = 120 - total_events.at[index, 'x']
            total_events.at[index, 'y'] = 80 - total_events.at[index, 'y']
            total_events.at[index, 'ex'] = 120 - total_events.at[index, 'ex']
            total_events.at[index, 'ey'] = 80 - total_events.at[index, 'ey']
            

    need_different = ['Forward', 'Side Back', 'Dribble', 'Cross', 'Long', 'Ground GK', 'Throw']
    total_events.dropna(subset=['x'], inplace=True)

    total_events = total_events.loc[total_events['Action'].isin(need_different)]

    def filter_rows(row):
        action = row['Action']
        if action in need_different:
            if row['x'] == row['ex'] or row['y'] == row['ey']:
                return False  # Delete the row
        return True  # Keep the row

    # Apply the filter function to each row
    total_events = total_events[total_events.apply(filter_rows, axis=1)].reset_index(drop=True)

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

    total_events['x1_bin'] = pd.cut(total_events['x'], bins=x_bins, labels=False, include_lowest=True)
    total_events['y1_bin'] = pd.cut(total_events['y'], bins=y_bins, labels=False, include_lowest=True)
    total_events['x2_bin'] = pd.cut(total_events['ex'], bins=ex_bins, labels=False, include_lowest=True)
    total_events['y2_bin'] = pd.cut(total_events['ey'], bins=ey_bins, labels=False, include_lowest=True)
    

    total_events.dropna(subset=['x1_bin', 'y1_bin', 'x2_bin', 'y2_bin'], inplace=True)
    total_events.reset_index(drop=True)
    total_events['y1_bin'] = total_events['y1_bin'].astype(int)
    total_events['y2_bin'] = total_events['y2_bin'].astype(int)
    total_events['x1_bin'] = total_events['x1_bin'].astype(int)
    total_events['x2_bin'] = total_events['x2_bin'].astype(int)
    total_events['start_zone_value'] = total_events[['x1_bin', 'y1_bin']].apply(lambda x: xT[x[1], x[0]], axis=1)
    total_events['end_zone_value'] = total_events[['x2_bin', 'y2_bin']].apply(lambda x: xT[x[1], x[0]], axis=1)

    total_events['xT'] = total_events['end_zone_value'] - total_events['start_zone_value']

    team_sum = total_events.groupby(['Team', 'Opposition', 'Match Date'])['xT'].sum()

    player_sum = total_events.groupby('Player Full Name')['xT'].sum()

    return team_sum, player_sum