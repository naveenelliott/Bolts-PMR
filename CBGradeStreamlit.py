import pandas as pd
import numpy as np
from scipy.stats import norm
from datetime import datetime
import streamlit as st

def CBFunction(dataframe):
    number_columns = ['mins played', 'Yellow Card', 'Red Card', 'Goal', 'Assist', 'Dribble',
           'Goal Against', 'Stand. Tackle', 'Unsucc Stand. Tackle', 'Tackle', 'Def Aerial', 'Unsucc Def Aerial',
           'Own Box Clear', 'Progr Rec', 'Unprogr Rec', 'Progr Inter', 'Unprogr Inter', 'Blocked Shot',
           'Blocked Cross', 'Att 1v1', 'Efforts on Goal', 'Shot on Target', 'Att Shot Blockd',
           'Long', 'Unsucc Long', 'Forward', 'Unsucc Forward', 'Line Break', 'Clear', 'Unsucc Tackle',
           'Loss of Poss', 'Success', 'Unsuccess', 'Foul Conceded', 'Progr Regain ', 'Stand. Tackle Success ', 
           'Def Aerial Success ', 'Pass Completion ', 'Progr Pass Attempt ', 'Progr Pass Completion ', 
           'PK Missed', 'PK Scored']

    details = dataframe.loc[:, ['Player Full Name', 'Team Name', 'Match Date', 'Position Tag', 'Starts']]
    #details = selected.loc[:, ['Player Full Name', 'Team Name', 'As At Date', 'Position Tag']]
    details.reset_index(drop=True, inplace=True)
    selected = dataframe.loc[:, ~dataframe.columns.duplicated()]
    selected_p90 = selected.loc[:, number_columns].astype(float)


    per90 = ['Yellow Card', 'Red Card', 'Goal', 'Assist', 'Dribble',
           'Stand. Tackle', 'Unsucc Stand. Tackle', 'Tackle', 'Def Aerial', 'Unsucc Def Aerial',
           'Own Box Clear', 'Progr Rec', 'Unprogr Rec', 'Progr Inter', 'Unprogr Inter', 'Blocked Shot',
           'Blocked Cross', 'Att 1v1', 'Efforts on Goal', 'Clear', 'Unsucc Tackle',
           'Shot on Target', 'Att Shot Blockd',
           'Long', 'Unsucc Long', 'Forward', 'Unsucc Forward', 'Line Break',
           'Loss of Poss', 'Success', 'Unsuccess', 'Foul Conceded', 'PK Missed', 'PK Scored']

    selected_p90['minutes per 90'] = selected_p90['mins played']/90

    for column in per90:
        if column not in ['Goal', 'Assist', 'Shot on Target', 'Yellow Card', 'Red Card', 'PK Missed', 'PK Scored']:
            selected_p90[column] = selected_p90[column] / selected_p90['minutes per 90']

    selected_p90 = selected_p90.drop(columns=['minutes per 90'])
    selected_p90.reset_index(drop=True, inplace=True)
    selected_p90.fillna(0, inplace=True)

    total_def_actions_columns = ['Tackle', 'Clear', 'Progr Inter', 'Unprogr Inter', 'Progr Rec', 
                             'Unprogr Rec', 'Stand. Tackle', 'Unsucc Stand. Tackle', 
                             'Unsucc Tackle']
    selected_p90['Total Def Actions'] = selected_p90[total_def_actions_columns].sum(axis=1)
    total_actions = selected_p90['Total Def Actions']
    total_actions.fillna(0, inplace=True)

    passing = selected_p90[['Pass Completion ']]
    passing.fillna(0, inplace=True)

    defending = selected_p90[['Progr Regain ']]
    defending.fillna(0, inplace=True)

    selected_p90['Def Aerial %'] = (selected_p90['Def Aerial']/(selected_p90['Def Aerial'] + selected_p90['Unsucc Def Aerial'])) * 100
    aerial = selected_p90[['Def Aerial %']]
    aerial.fillna(0, inplace=True)

    selected_p90['Forward Passes'] = selected_p90['Forward'] + selected_p90['Unsucc Forward']
    progression = selected_p90[['Forward Passes', 'Progr Pass Completion ']]

    adjustments = selected_p90[['Yellow Card', 'Red Card', 'Goal', 'Assist',
                                'Def Aerial', 'Unsucc Def Aerial', 'PK Missed', 'PK Scored']]

    for index, row in adjustments.iterrows():
        if adjustments['PK Scored'][index] == 1:
            adjustments['Goal'][index] = adjustments['Goal'][index] - 1
        elif adjustments['PK Scored'][index] == 2:
            adjustments['Goal'][index] = adjustments['Goal'][index] - 2
    adjustments.fillna(0, inplace=True)
    adjustments['Yellow Card'] = adjustments['Yellow Card'] * -.5
    adjustments['Red Card'] = adjustments['Red Card'] * -2
    adjustments['Goal'] = adjustments['Goal'] * 1.5
    adjustments['Assist'] = adjustments['Assist'] * 1
    adjustments['Def Aerial'] = adjustments['Def Aerial'] * 0.025
    adjustments['Unsucc Def Aerial'] = adjustments['Unsucc Def Aerial'] * -.05
    adjustments['PK Missed'] = adjustments['PK Missed'] * -1
    adjustments['PK Scored'] = adjustments['PK Scored'] * 0.7
     

    def calculate_percentile(value):
        return norm.cdf(value) * 100

    # Function to calculate z-score for each element in a column
    def calculate_zscore(column, mean, std):
        return (column - mean) / std

    def clip_percentile(value):
        return max(min(value, 100), 50)

    player_location = []
    for index, row in details.iterrows():
        if 'RCB' in row['Position Tag']:
            player_location.append(index)
        elif 'LCB' in row['Position Tag']:
            player_location.append(index)
        elif 'CB' in row['Position Tag']:
            player_location.append(index)
            
    readding = []
    selected_p90 = pd.concat([details, selected_p90], axis=1)
    final = pd.DataFrame()

    for i in player_location:
        more_data = selected_p90.iloc[i]
        player_name = selected_p90['Player Full Name'][i]
        team_name = more_data['Team Name']
        date = more_data['Match Date']
        
        if ('U13' in team_name) or ('U14' in team_name):
            cb_df = pd.read_csv("Thresholds/CenterBackThresholds1314.csv")
        elif ('U15' in team_name) or ('U16' in team_name):
            cb_df = pd.read_csv("Thresholds/CenterBackThresholds1516.csv")
        elif ('U17' in team_name) or ('U19' in team_name):
            cb_df = pd.read_csv("Thresholds/CenterBackThresholds1719.csv")
        

        mean_values = cb_df.iloc[0, 2]
        std_values = cb_df.iloc[1, 2]
        # Calculate the z-score for each data point
        z_scores_df = passing.transform(lambda col: calculate_zscore(col, mean_values, std_values))
        passing_percentile = z_scores_df.map(calculate_percentile)
        passing_percentile = passing_percentile.map(clip_percentile)
        player_passing = passing_percentile.iloc[player_location]
        weights = np.array([0.1])
        passing_score = (
            player_passing['Pass Completion '] * weights[0]
            )

        mean_values = cb_df.iloc[0, 1]
        std_values = cb_df.iloc[1, 1]
        # Calculate the z-score for each data point
        z_scores_df = defending.transform(lambda col: calculate_zscore(col, mean_values, std_values))
        defending_percentile = z_scores_df.map(calculate_percentile)
        defending_percentile = defending_percentile.map(clip_percentile)
        player_defending = defending_percentile.iloc[player_location] 
        weights = np.array([.1])
        defending_score = (
            player_defending['Progr Regain '] * weights[0]
            )   

        mean_values = cb_df.iloc[0, 3]
        std_values = cb_df.iloc[1, 3]
        # Calculate the z-score for each data point
        z_scores_df = aerial.transform(lambda col: calculate_zscore(col, mean_values, std_values))
        aerial_percentile = z_scores_df.map(calculate_percentile)
        aerial_percentile = aerial_percentile.map(clip_percentile)
        player_aerial = aerial_percentile.iloc[player_location].reset_index()
        weights = np.array([.1])
        aerial_score = (
            player_aerial['Def Aerial %'] * weights[0]
            )
        
        mean_values = cb_df.iloc[0, 0]
        std_values = cb_df.iloc[1, 0]
        # Calculate the z-score for each data point
        z_scores_df = total_actions.transform(lambda col: calculate_zscore(col, mean_values, std_values))
        total_actions_percentile = z_scores_df.map(calculate_percentile)
        total_actions_percentile = total_actions_percentile.map(clip_percentile)
        player_ta = total_actions_percentile.iloc[player_location].reset_index()
        weights = np.array([.1])
        ta_score = (
            player_ta['Total Def Actions'] * weights[0]
            )
        
        mean_values = cb_df.iloc[0, [4, 5]]
        std_values = cb_df.iloc[1, [4, 5]]
        # Calculate the z-score for each data point
        z_scores_df = progression.transform(lambda col: calculate_zscore(col, mean_values[col.name], std_values[col.name]))
        progression_percentile = z_scores_df.map(calculate_percentile)
        progression_percentile = progression_percentile.map(clip_percentile)
        player_prog = progression_percentile.iloc[player_location].reset_index()
        weights = np.array([.05, .05])
        prog_score = (
            player_prog['Forward Passes'] * weights[0] + 
            player_prog['Progr Pass Completion '] * weights[1]
            )

        add = adjustments.iloc[i, :].sum()
        readding.append(add)

        
        final_grade = (defending_score * .2) + (passing_score * .2) + (aerial_score * .2) + (ta_score * .2) * (prog_score * 0.2)
        final['Final Grade'] = final_grade
        final['Passing'] = passing_score
        final['Defending'] = defending_score
        final['Aerial'] = aerial_score
        final['Total Def Actions'] = ta_score
        final['Team Name'] = team_name
        final['Date'] = date
    

    player_name = []
    player_minutes = []
    player_position = []
    player_starts = []
    for i in player_location:
         player_name.append(selected_p90['Player Full Name'][i])
         player_minutes.append(selected_p90['mins played'][i])
         player_position.append(selected_p90['Position Tag'][i])
         player_starts.append(selected_p90['Starts'][i])
    final['Minutes'] = player_minutes
    final['Player Name'] = player_name
    final['Position'] = player_position
    final['Started'] = player_starts
    final['Adjustments'] = readding
    
    return final
