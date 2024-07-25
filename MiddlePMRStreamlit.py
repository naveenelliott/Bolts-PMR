import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from fuzzywuzzy import process
import datetime
import numpy as np
import streamlit as st
from GettingPSDTeamData import getting_PSD_team_data

#team='Boston Bolts U13'
#opp='Seacoast'
#date=datetime.datetime(2024, 4, 28)
#date = date.strftime('%m/%d/%Y')


def GettingCompLevel(team, opp, date):
    raw_data = pd.read_csv("Veo Data/Veo Analysis - Formatted Games.csv")
    raw_data.dropna(inplace=True)
    raw_data['Date'] = pd.to_datetime(raw_data['Date'])
    raw_data['Date'] = raw_data['Date'].dt.strftime('%m/%d/%Y')
    age_group_map = {
    'U13': 'Boston Bolts U13',
    'U14': 'Boston Bolts U14',
    'U15': 'Boston Bolts U15',
    'U16': 'Boston Bolts U16',
    'U17': 'Boston Bolts U17',
    'U19': 'Boston Bolts U19'
    }

    def map_age_group(opponent):
        for age_group, team_name in age_group_map.items():
            if age_group in opponent:
                return team_name
        return 'Unknown'  # Default value if no age group found

    # Create the 'Team' column based on the 'Opponent' column
    raw_data['Team'] = raw_data['Opponent'].apply(map_age_group)
    age_groups = ['U13', 'U14', 'U15', 'U16', 'U17', 'U19']
    for age_group in age_groups:
        raw_data['Opponent'] = raw_data['Opponent'].str.replace(age_group, '').str.strip()
    raw_data = raw_data[raw_data['Team'] == team]
    raw_data = raw_data[raw_data['Opponent'] == opp]
    raw_data = raw_data[raw_data['Date'] == date]
    raw_data.reset_index(drop=True, inplace=True)
    value_wanted = raw_data['Competition'][0]
    return value_wanted


def MiddlePMRStreamlit(team, opp, date, avg_opp_xg, avg_bolts_xg, our_xT, avg_xT, stdev_xT, regain_time):
    raw_data = pd.read_csv("Veo Data/Veo Analysis - Formatted Games.csv")
    raw_data.drop(columns=['Competition'], inplace=True)
    raw_data.dropna(inplace=True)
    raw_data['Date'] = pd.to_datetime(raw_data['Date'])
    raw_data['Date'] = raw_data['Date'].dt.strftime('%m/%d/%Y')
    age_group_map = {
    'U13': 'Boston Bolts U13',
    'U14': 'Boston Bolts U14',
    'U15': 'Boston Bolts U15',
    'U16': 'Boston Bolts U16',
    'U17': 'Boston Bolts U17',
    'U19': 'Boston Bolts U19'
    }

    def map_age_group(opponent):
        for age_group, team_name in age_group_map.items():
            if age_group in opponent:
                return team_name
        return 'Unknown'  # Default value if no age group found

    # Create the 'Team' column based on the 'Opponent' column
    raw_data['Team'] = raw_data['Opponent'].apply(map_age_group)
    age_groups = ['U13', 'U14', 'U15', 'U16', 'U17', 'U19']
    for age_group in age_groups:
        raw_data['Opponent'] = raw_data['Opponent'].str.replace(age_group, '').str.strip()
    raw_data = raw_data[raw_data['Team'] == team]
    raw_data = raw_data[raw_data['Opponent'] == opp]
    raw_data = raw_data[raw_data['Date'] == date]
    actual_raw = raw_data.loc[:, ['Date', 'Passes per Minute (in Possession)', 'Possession ']]



    sa_average= 9.5
    sa_std = 2
    ppm_average = 2.5
    ppm_std = .52
    poss_average = 48
    poss_std = 6
    regain_average = 25
    regain_std = 4

    team_data = getting_PSD_team_data()
    cols_we_want = ['Date', 'Team Name', 'Opposition', 'Pass Completion ', 'Goal Against',
           'Efforts on Goal', 'Opp Effort on Goal']
    team_data = team_data[cols_we_want]
    team_data['Date'] = pd.to_datetime(team_data['Date'])  
    team_data['Date'] = team_data['Date'].dt.strftime('%m/%d/%Y')
    team_data = team_data.loc[team_data['Team Name'] == team]
    team_data = team_data.loc[team_data['Opposition'] == opp]
    team_data.drop(columns={'Team Name', 'Opposition'}, inplace=True)

    raw_data['Passes per Minute (in Possession)'] = raw_data['Passes per Minute (in Possession)'].astype(float)
    raw_data['Passes per Minute (in Possession)'] = ((raw_data['Passes per Minute (in Possession)'] - ppm_average) / ppm_std) * 2 + 5
    raw_data['Passes per Minute (in Possession)'] = round(raw_data['Passes per Minute (in Possession)'].clip(1, 10), 2)
    raw_data['Possession '] = raw_data['Possession '].str.replace('%', '').astype(float)
    raw_data['Possession '] = ((raw_data['Possession '] - poss_average) / poss_std) * 2 + 5
    raw_data['Possession '] = raw_data['Possession '].clip(1, 10)
    team_data.reset_index(drop=True, inplace=True)
    raw_data.reset_index(drop=True, inplace=True)
    if pd.isna(team_data['Opp Effort on Goal']).any():
        raw_data = raw_data.loc[:, ['Date', 'Passes per Minute (in Possession)', 'Opp Shots', 'Possession ', 'Goal Differential', 'Win/Loss/Draw Adjustment', 'Competition Adjustment (1 = Playoffs, 2 = MLS Flex Event, 3 = Team Sucks)']] 
        team_data['Opp Effort on Goal'] = raw_data['Opp Shots']
        raw_data.drop(columns={'Opp Shots'}, inplace=True)
    else:    
        raw_data = raw_data.loc[:, ['Date', 'Passes per Minute (in Possession)', 'Possession ', 'Goal Differential', 'Win/Loss/Draw Adjustment', 'Competition Adjustment (1 = Playoffs, 2 = MLS Flex Event, 3 = Team Sucks)']] 

    
    important = pd.merge(raw_data, team_data, on='Date', how='inner')
    important['xT per 90'] = np.nan
    important.at[0, 'xT per 90'] = our_xT
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
        if row['Competition Adjustment (1 = Playoffs, 2 = MLS Flex Event, 3 = Team Sucks)'] == 1:
            adjustments.append(1)
        elif row['Competition Adjustment (1 = Playoffs, 2 = MLS Flex Event, 3 = Team Sucks)'] == 3:
            adjustments.append(-1)
        

    total = sum(adjustments)

    mean_xG_opp = avg_opp_xg
    mean_xG = avg_bolts_xg

    raw_labels = pd.merge(actual_raw, team_data, on='Date', how='inner')
    raw_labels.drop(columns=['Date'], inplace=True)
    pass_average = 80
    pass_std = 3.43
    shots_average = 11
    shots_std = 3
    ga_average = 1.5
    ga_std = .75
    sa_average= 9.5
    sa_std = 2.5
    xg_per_shot_bolts_avg = 0.255
    xg_per_shot_bolts_std = 0.06021
    xg_per_shot_opp = 0.25
    xg_per_shot_opp_std = 0.05


    important['xG per Shot'] = ((mean_xG - xg_per_shot_bolts_avg) / xg_per_shot_bolts_std) * 2 + 5
    important['xG per Shot'] = important['xG per Shot'].clip(1, 10)
    important['Opponent xG per Shot'] = ((mean_xG_opp - xg_per_shot_opp) / xg_per_shot_opp_std) * 2 + 5
    important['Opponent xG per Shot'] = 11 - important['Opponent xG per Shot'].clip(1, 10)
    important['Efforts on Goal'] = ((important['Efforts on Goal'] - shots_average) / shots_std) * 2 + 5
    important['Efforts on Goal'] = important['Efforts on Goal'].clip(1, 10)
    important['Opp Effort on Goal'] = ((important['Opp Effort on Goal'] - sa_average) / sa_std) * 2 + 5
    important['Opp Effort on Goal'] = 11 - important['Opp Effort on Goal'].clip(1, 10)
    important['xT per 90'] = ((important['xT per 90'] - avg_xT) / stdev_xT) * 2 + 5
    important['xT per 90'] = important['xT per 90'].clip(1, 10)
    important['Time Until Regain'] = ((important['Time Until Regain'] - regain_average) / regain_std) * 2 + 5
    important['Time Until Regain'] = 11 - important['Time Until Regain'].clip(1, 10)
    average_columns = ['Efforts on Goal', 'Opp Effort on Goal', 'Possession ', 
                       'xG per Shot', 'Opponent xG per Shot', 'xT per 90', 'Time Until Regain']
    important['Final Rating'] = important[average_columns].mean(axis=1) + total
    if important['Final Rating'][0] > 10:
        important['Final Rating'][0] = 10


    actual_raw = pd.merge(actual_raw, team_data, on='Date')


    row_series = actual_raw.iloc[0]

    important.drop(columns=['Win/Loss/Draw Adjustment', 'Goal Differential', 
                            'Competition Adjustment (1 = Playoffs, 2 = MLS Flex Event, 3 = Team Sucks)'], inplace=True)

    first_row = important.iloc[0]
    first_row[~first_row.index.isin(['Date'])] *= 10

    # Update the first row in the DataFrame
    important.iloc[0] = first_row

    row_series['xG per Shot'] = mean_xG
    row_series['Opponent xG per Shot'] = mean_xG_opp
    row_series['xT per 90'] = our_xT[0]
    row_series['Time Until Regain'] = regain_time
    row_series['Date'] = date
    row_series['Final Rating'] = ''
    
    row_series = row_series.to_frame()
    row_series = row_series.T
    row_series.index = row_series.index + 1
    
    important = pd.concat([important, row_series], ignore_index=True)

    important.drop(columns='Date', inplace=True)
    important.rename(columns={'Passes per Minute (in Possession)': 'Passes per Min', 
                              'Possession ': 'Possession', 
                              'Pass Completion ': 'Pass %', 
                              'Efforts on Goal': 'Shots', 
                              'Opp Effort on Goal': 'Opp Shots', 
                              'Opponent xG per Shot': 'Opp xG per Shot', 
                              'Goal Against': 'Goals Against'}, inplace=True)
    # Round to nearest 10
    def round_to_nearest_10(num):
        return round(num / 10) * 10

    new_order = ['Possession', 'xT per 90', 'Shots',
          'xG per Shot', 'Time Until Regain', 'Opp Shots', 'Opp xG per Shot', 'Final Rating']
    important = important[new_order]

    

    raw_vals = important.copy()
    raw_vals.iloc[0] = raw_vals.iloc[0].astype(float).apply(round)
    raw_vals.at[1, 'xG per Shot'] = round(raw_vals.at[1, 'xG per Shot'], 3)
    raw_vals.at[1, 'Opp xG per Shot'] = round(raw_vals.at[1, 'Opp xG per Shot'], 3)
    raw_vals.at[1, 'xT per 90'] = round(raw_vals.at[1, 'xT per 90'], 3)
    raw_vals.at[1, 'Time Until Regain'] = round(raw_vals.at[1, 'Time Until Regain'], 2)
    important.iloc[0] = important.iloc[0].apply(round_to_nearest_10)

    dummy_df = pd.DataFrame(columns=important.columns)
    for i in range(10):
        i = i + 1
        dummy_df.loc[i] = [i * 10] * len(important.columns)

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
    plt.xticks([10, 20, 30, 40, 50, 60, 70, 80, 90, 100], fontsize=14)
    plt.yticks(fontsize=14)
    return fig
