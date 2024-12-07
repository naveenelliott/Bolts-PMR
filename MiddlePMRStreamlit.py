import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from GettingPSDTeamData import getting_PSD_team_data


def MiddlePMRStreamlit(team, opp, date, avg_opp_xg, avg_bolts_xg, regain_time):
    
    sa_average= 9.5
    sa_std = 2
    poss_average = 48
    poss_std = 6
    regain_average = 25
    regain_std = 4
    pass_in_18_average = 14
    pass_in_18_std = 7.47

    team_data = getting_PSD_team_data()
    cols_we_want = ['Date', 'Team Name', 'Opposition', 'Goal Against',
           'Efforts on Goal', 'Opp Effort on Goal', 'Goal', 'Pass Completion ', 'Pass into Oppo Box']
    team_data = team_data[cols_we_want]
    team_data['Date'] = pd.to_datetime(team_data['Date']).dt.strftime('%m/%d/%Y')
    team_data = team_data.loc[(team_data['Team Name'] == team) & (team_data['Opposition'] == opp) & (team_data['Date'] == date)]

    if team_data['Opp Effort on Goal'].isna().any():
        # Drop the column if it contains NA values
        team_data = team_data.drop(columns=['Opp Effort on Goal'])

    if (team == 'Boston Bolts U14 NALB' and 
        opp == 'Seacoast of Bedford Seacoast United Bedford' and 
        date == '09/21/2024'):
        team_data['Goal Against'] += 1 

    team_data['Goal Differential'] = team_data['Goal'] - team_data['Goal Against']

    team_data['Win/Loss/Draw Adjustment'] = 0
    for index, row in team_data.iterrows():
        if row['Goal Differential'] > 0:
            team_data.at[index, 'Win/Loss/Draw Adjustment'] = 1
        elif row['Goal Differential'] == 0:
            team_data.at[index, 'Win/Loss/Draw Adjustment'] = 0.5

    team_data.drop(columns={'Team Name', 'Opposition'}, inplace=True)
    team_data.reset_index(drop=True, inplace=True)
    
    important = team_data.copy()
    important.at[0, 'Time Until Regain'] = regain_time

    adjustments = []
    for index, row in important.iterrows():
        if row['Goal Differential'] >= 2:
            adjustments.append(1.5)
        elif row['Goal Differential'] <= -2:
            adjustments.append(-1.5)
        if row['Win/Loss/Draw Adjustment'] > 0.5:
            adjustments.append(1)
        elif row['Win/Loss/Draw Adjustment'] < 0.5:
            adjustments.append(-1)
        

    total = sum(adjustments)

    mean_xG_opp = avg_opp_xg
    mean_xG = avg_bolts_xg

    raw_labels = team_data.copy()
    raw_labels.drop(columns=['Date'], inplace=True)
    shots_average = 11
    shots_std = 3
    sa_average= 9.5
    sa_std = 2.5
    xg_per_shot_bolts_avg = 0.19652
    xg_per_shot_bolts_std = 0.09712
    xg_per_shot_opp = 0.1587
    xg_per_shot_opp_std = 0.0531
    pass_average = 80
    pass_std = 3.43


    important['xG per Shot'] = ((mean_xG - xg_per_shot_bolts_avg) / xg_per_shot_bolts_std) * 2 + 5
    important['xG per Shot'] = important['xG per Shot'].clip(1, 10)
    important['Opponent xG per Shot'] = ((mean_xG_opp - xg_per_shot_opp) / xg_per_shot_opp_std) * 2 + 5
    important['Opponent xG per Shot'] = 11 - important['Opponent xG per Shot'].clip(1, 10)
    important['Efforts on Goal'] = ((important['Efforts on Goal'] - shots_average) / shots_std) * 2 + 5
    important['Efforts on Goal'] = important['Efforts on Goal'].clip(1, 10)
    if 'Opp Effort on Goal' in important.columns:
        important['Opp Effort on Goal'] = ((important['Opp Effort on Goal'] - sa_average) / sa_std) * 2 + 5
        important['Opp Effort on Goal'] = 11 - important['Opp Effort on Goal'].clip(1, 10)
    important['Time Until Regain'] = ((important['Time Until Regain'] - regain_average) / regain_std) * 2 + 5
    important['Time Until Regain'] = 11 - important['Time Until Regain'].clip(1, 10)
    important['Pass Completion '] = ((important['Pass Completion '] - pass_average) / pass_std) * 2 + 5
    important['Pass Completion '] = important['Pass Completion '].clip(1, 10)
    important['Pass into Oppo Box'] = ((important['Pass into Oppo Box'] - pass_in_18_average) / pass_in_18_std) * 2 + 5
    important['Pass into Oppo Box'] = important['Pass into Oppo Box'].clip(1, 10)
    average_columns = ['Efforts on Goal',
                       'xG per Shot', 'Opponent xG per Shot', 'Time Until Regain', 'Pass Completion ', 'Pass into Oppo Box']
    if 'Opp Effort on Goal' in important.columns:
        average_columns.insert(1, 'Opp Effort on Goal')
    important['Final Rating'] = important[average_columns].mean(axis=1) + total
    if important['Final Rating'][0] > 10:
        important['Final Rating'][0] = 10


    actual_raw = team_data.copy()


    row_series = actual_raw.iloc[0]

    important.drop(columns=['Win/Loss/Draw Adjustment', 'Goal Differential'], inplace=True)

    first_row = important.iloc[0]
    first_row[~first_row.index.isin(['Date'])] *= 10

    # Update the first row in the DataFrame
    important.iloc[0] = first_row

    row_series['xG per Shot'] = mean_xG
    row_series['Opponent xG per Shot'] = mean_xG_opp
    row_series['Time Until Regain'] = regain_time
    row_series['Date'] = date
    row_series['Final Rating'] = ''
    
    row_series = row_series.to_frame()
    row_series = row_series.T
    row_series.index = row_series.index + 1
    
    important = pd.concat([important, row_series], ignore_index=True)

    important.drop(columns='Date', inplace=True)
    if 'Opp Effort on Goal' in important.columns:
        important.rename(columns={
                              'Efforts on Goal': 'Shots', 
                              'Opp Effort on Goal': 'Opp Shots', 
                              'Opponent xG per Shot': 'Opp xG per Shot', 
                              'Pass Completion ': 'Pass %', 
                              'Pass into Oppo Box': 'Passes into 18'}, inplace=True)
    else:
        important.rename(columns={
                              'Efforts on Goal': 'Shots',
                              'Opponent xG per Shot': 'Opp xG per Shot', 
                              'Pass Completion ': 'Pass %', 
                              'Pass into Oppo Box': 'Passes into 18'}, inplace=True)
    # Round to nearest 10
    def round_to_nearest_10(num):
        return round(num / 10) * 10

    new_order = ['Passes into 18', 'Pass %', 'Shots',
          'xG per Shot', 'Time Until Regain', 'Opp xG per Shot', 'Final Rating']
    if 'Opp Shots' in important.columns:
        new_order.insert(4, 'Opp Shots')
    important = important[new_order]

    

    raw_vals = important.copy()
    raw_vals.iloc[0] = raw_vals.iloc[0].astype(float).apply(round)
    raw_vals.at[1, 'xG per Shot'] = round(raw_vals.at[1, 'xG per Shot'], 3)
    raw_vals.at[1, 'Opp xG per Shot'] = round(raw_vals.at[1, 'Opp xG per Shot'], 3)
    raw_vals.at[1, 'Time Until Regain'] = round(raw_vals.at[1, 'Time Until Regain'], 2)
    important.iloc[0] = important.iloc[0].apply(round_to_nearest_10)

    dummy_df = pd.DataFrame(columns=important.columns)
    for i in range(11):
        dummy_df.loc[i] = [i * 10] * len(important.columns)
        i = i + 1

    fig, ax = plt.subplots(figsize=(6, 5))
    for index, row in dummy_df.iterrows():
        ax.scatter(row, dummy_df.columns, c='#D3D3D3', s=160)
    ax.scatter(important.iloc[0], important.columns, c='#6bb2e2', s=175, edgecolors='black')
    for i, col in enumerate(raw_vals.columns):
        if pd.isna(raw_vals.iloc[1][col]):
            raw_vals.iloc[1][col] = ''
        raw_val_0 = raw_vals.iloc[0][col]
        raw_val_1 = raw_vals.iloc[1][col] if not pd.isna(raw_vals.iloc[1][col]) else ''
        text = f'{raw_val_0} ({raw_val_1})'
        
        # Split the text into two parts
        part1 = f'{raw_val_0} '
        part2 = f'({raw_val_1})'
        
        # Add the first part of the text
        text_obj = ax.text(110, i, part1, verticalalignment='center', fontsize=12, color='#6bb2e2')

        # Get the bounding box of the first text part in display coordinates
        bbox = text_obj.get_window_extent(renderer=fig.canvas.get_renderer())

        # Calculate the new x position for the second text part in data coordinates
        display_coords = bbox.transformed(ax.transData.inverted())
        new_x = display_coords.x1

        # Add the second part of the text
        ax.text(new_x, i, part2, verticalalignment='center', fontsize=12, color='black')

    # Customize the plot
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.xticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], fontsize=14)
    plt.yticks(fontsize=14)
    return fig

def MiddlePMRStreamlit_NALOlder(team, opp, date, regain_time):
    
    sa_average= 9.5
    sa_std = 2
    poss_average = 48
    poss_std = 6
    regain_average = 25
    regain_std = 4
    pass_in_18_average = 14
    pass_in_18_std = 7.47

    team_data = getting_PSD_team_data()
    cols_we_want = ['Date', 'Team Name', 'Opposition', 'Goal Against',
                   'Efforts on Goal', 'Opp Effort on Goal', 'Goal', 'Pass Completion ', 'Pass into Oppo Box', 
                   'Shots on Target Against', 'Header on Target', 'Shot on Target']
    team_data = team_data[cols_we_want]
    team_data['Date'] = pd.to_datetime(team_data['Date']).dt.strftime('%m/%d/%Y')
    team_data = team_data.loc[(team_data['Team Name'] == team) & (team_data['Opposition'] == opp) & (team_data['Date'] == date)]

    required_columns = ['Shots on Target Against', 'Header on Target', 'Shot on Target']
    team_data[required_columns] = team_data[required_columns].apply(pd.to_numeric, errors='coerce')
    
    game_opponent_sot = team_data['Shots on Target Against'].sum()
    game_bolts_sot = team_data['Header on Target'].sum() + team_data['Shot on Target'].sum()
    
    if team_data['Opp Effort on Goal'].isna().any():
        # Drop the column if it contains NA values
        team_data = team_data.drop(columns=['Opp Effort on Goal'])

    if (team == 'Boston Bolts U14 NALB' and 
        opp == 'Seacoast of Bedford Seacoast United Bedford' and 
        date == '09/21/2024'):
        team_data['Goal Against'] += 1 

    team_data['Goal Differential'] = team_data['Goal'] - team_data['Goal Against']

    team_data['Win/Loss/Draw Adjustment'] = 0
    for index, row in team_data.iterrows():
        if row['Goal Differential'] > 0:
            team_data.at[index, 'Win/Loss/Draw Adjustment'] = 1
        elif row['Goal Differential'] == 0:
            team_data.at[index, 'Win/Loss/Draw Adjustment'] = 0.5

    team_data.drop(columns={'Team Name', 'Opposition'}, inplace=True)
    team_data.reset_index(drop=True, inplace=True)
    
    important = team_data.copy()
    important.at[0, 'Time Until Regain'] = regain_time

    adjustments = []
    for index, row in important.iterrows():
        if row['Goal Differential'] >= 2:
            adjustments.append(1.5)
        elif row['Goal Differential'] <= -2:
            adjustments.append(-1.5)
        if row['Win/Loss/Draw Adjustment'] > 0.5:
            adjustments.append(1)
        elif row['Win/Loss/Draw Adjustment'] < 0.5:
            adjustments.append(-1)
        

    total = sum(adjustments)

    raw_labels = team_data.copy()
    raw_labels.drop(columns=['Date'], inplace=True)
    shots_average = 11
    shots_std = 3
    sa_average= 9.5
    sa_std = 2.5
    sot_average = 6.49
    sot_std = 3.44
    opp_sot_average = 5.47
    opp_sot_std = 2.93
    pass_average = 80
    pass_std = 3.43


    important['Bolts SOT'] = ((game_bolts_sot - sot_average) / sot_std) * 2 + 5
    important['Bolts SOT'] = important['Bolts SOT'].clip(1, 10)
    important['Opponent SOT'] = ((game_opponent_sot - opp_sot_average) / opp_sot_std) * 2 + 5
    important['Opponent SOT'] = 11 - important['Opponent SOT'].clip(1, 10)
    important['Efforts on Goal'] = ((important['Efforts on Goal'] - shots_average) / shots_std) * 2 + 5
    important['Efforts on Goal'] = important['Efforts on Goal'].clip(1, 10)
    if 'Opp Effort on Goal' in important.columns:
        important['Opp Effort on Goal'] = ((important['Opp Effort on Goal'] - sa_average) / sa_std) * 2 + 5
        important['Opp Effort on Goal'] = 11 - important['Opp Effort on Goal'].clip(1, 10)
    important['Time Until Regain'] = ((important['Time Until Regain'] - regain_average) / regain_std) * 2 + 5
    important['Time Until Regain'] = 11 - important['Time Until Regain'].clip(1, 10)
    important['Pass Completion '] = ((important['Pass Completion '] - pass_average) / pass_std) * 2 + 5
    important['Pass Completion '] = important['Pass Completion '].clip(1, 10)
    important['Pass into Oppo Box'] = ((important['Pass into Oppo Box'] - pass_in_18_average) / pass_in_18_std) * 2 + 5
    important['Pass into Oppo Box'] = important['Pass into Oppo Box'].clip(1, 10)
    average_columns = ['Efforts on Goal',
                       'Bolts SOT', 'Opponent SOT', 'Time Until Regain', 'Pass Completion ', 'Pass into Oppo Box']
    if 'Opp Effort on Goal' in important.columns:
        average_columns.insert(1, 'Opp Effort on Goal')
    important['Final Rating'] = important[average_columns].mean(axis=1) + total
    if important['Final Rating'][0] > 10:
        important['Final Rating'][0] = 10


    actual_raw = team_data.copy()


    row_series = actual_raw.iloc[0]

    important.drop(columns=['Win/Loss/Draw Adjustment', 'Goal Differential'], inplace=True)

    first_row = important.iloc[0]
    first_row[~first_row.index.isin(['Date'])] *= 10

    # Update the first row in the DataFrame
    important.iloc[0] = first_row

    row_series['Bolts SOT'] = game_bolts_sot
    row_series['Opponent SOT'] = game_opponent_sot
    row_series['Time Until Regain'] = regain_time
    row_series['Date'] = date
    row_series['Final Rating'] = ''
    
    row_series = row_series.to_frame()
    row_series = row_series.T
    row_series.index = row_series.index + 1
    
    important = pd.concat([important, row_series], ignore_index=True)

    important.drop(columns='Date', inplace=True)
    if 'Opp Effort on Goal' in important.columns:
        important.rename(columns={
                              'Efforts on Goal': 'Shots', 
                              'Opp Effort on Goal': 'Opp Shots', 
                              'Pass Completion ': 'Pass %', 
                              'Pass into Oppo Box': 'Passes into 18'}, inplace=True)
    else:
        important.rename(columns={
                              'Efforts on Goal': 'Shots',
                              'Pass Completion ': 'Pass %', 
                              'Pass into Oppo Box': 'Passes into 18'}, inplace=True)
    # Round to nearest 10
    def round_to_nearest_10(num):
        return round(num / 10) * 10

    new_order = ['Passes into 18', 'Pass %', 'Shots',
          'Bolts SOT', 'Time Until Regain', 'Opponent SOT', 'Final Rating']
    if 'Opp Shots' in important.columns:
        new_order.insert(4, 'Opp Shots')
    important = important[new_order]

    

    raw_vals = important.copy()
    raw_vals.iloc[0] = raw_vals.iloc[0].astype(float).apply(round)
    raw_vals.at[1, 'Time Until Regain'] = round(raw_vals.at[1, 'Time Until Regain'], 2)
    important.iloc[0] = important.iloc[0].apply(round_to_nearest_10)

    dummy_df = pd.DataFrame(columns=important.columns)
    for i in range(11):
        dummy_df.loc[i] = [i * 10] * len(important.columns)
        i = i + 1

    fig, ax = plt.subplots(figsize=(6, 5))
    for index, row in dummy_df.iterrows():
        ax.scatter(row, dummy_df.columns, c='#D3D3D3', s=160)
    ax.scatter(important.iloc[0], important.columns, c='#6bb2e2', s=175, edgecolors='black')
    for i, col in enumerate(raw_vals.columns):
        if pd.isna(raw_vals.iloc[1][col]):
            raw_vals.iloc[1][col] = ''
        raw_val_0 = raw_vals.iloc[0][col]
        raw_val_1 = raw_vals.iloc[1][col] if not pd.isna(raw_vals.iloc[1][col]) else ''
        text = f'{raw_val_0} ({raw_val_1})'
        
        # Split the text into two parts
        part1 = f'{raw_val_0} '
        part2 = f'({raw_val_1})'
        
        # Add the first part of the text
        text_obj = ax.text(110, i, part1, verticalalignment='center', fontsize=12, color='#6bb2e2')

        # Get the bounding box of the first text part in display coordinates
        bbox = text_obj.get_window_extent(renderer=fig.canvas.get_renderer())

        # Calculate the new x position for the second text part in data coordinates
        display_coords = bbox.transformed(ax.transData.inverted())
        new_x = display_coords.x1

        # Add the second part of the text
        ax.text(new_x, i, part2, verticalalignment='center', fontsize=12, color='black')

    # Customize the plot
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.xticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], fontsize=14)
    plt.yticks(fontsize=14)
    return fig

