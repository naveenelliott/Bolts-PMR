import pandas as pd
import numpy as np
from scipy.stats import norm
from datetime import datetime
import streamlit as st

def calculate_threshold(df, quantile, std_multiplier=2, std_adjustment=0.8):
    end_df = pd.DataFrame(columns=df.columns)
    
    for column in df.columns:
        # HERE IS THE ISSUE
        if df[column].quantile(quantile) < std_multiplier * df[column].std() * std_adjustment:
            threshold = df[column].mean()
        else:
            threshold = df[column].quantile(quantile)
        
        end_df[column] = [threshold]
    
    # Add a row with column standard deviations
    adjusted_std = df.std() * std_adjustment
    end_df.loc[len(end_df)] = adjusted_std
    
    return end_df



def WingerFunction(dataframe):
    number_columns = ['mins played', 'Yellow Card', 'Red Card', 'Goal', 'Assist', 'Dribble',
           'Goal Against', 'Stand. Tackle', 'Unsucc Stand. Tackle', 
           'Progr Rec', 'Unprogr Rec', 'Progr Inter', 'Unprogr Inter', 'Att 1v1', 'Efforts on Goal', 'Cross', 'Unsucc Cross',
           'Shot on Target', 'Pass into Oppo Box', 'Tackle', 'Clear', 'Unsucc Tackle',
           'Long', 'Unsucc Long', 'Forward', 'Unsucc Forward', 'Line Break', 
           'Loss of Poss', 'Success', 'Unsuccess',  'Foul Won', 'Progr Regain ', 'Stand. Tackle Success ', 'Def Aerial Success ',
           'Pass Completion ', 'Progr Pass Attempt ', 'Progr Pass Completion ', 'PK Missed', 'PK Scored']
    details = dataframe.loc[:, ['Player Full Name', 'Team Name', 'As At Date', 'Position Tag', 'Starts']]
    #details = selected.loc[:, ['Player Full Name', 'Team Name', 'As At Date', 'Position Tag']]
    details.reset_index(drop=True, inplace=True)

    selected_p90 = dataframe
    selected = dataframe.loc[:, ~dataframe.columns.duplicated()]
    selected_p90 = selected.loc[:, number_columns].astype(float)

    per90 = ['Yellow Card', 'Red Card', 'Goal', 'Assist', 'Dribble',
           'Stand. Tackle', 'Unsucc Stand. Tackle',
           'Progr Rec', 'Unprogr Rec', 'Progr Inter', 'Unprogr Inter',
           'Att 1v1', 'Efforts on Goal', 'Cross', 'Unsucc Cross',
           'Shot on Target', 'Pass into Oppo Box', 'Tackle', 'Clear', 'Unsucc Tackle',
           'Long', 'Unsucc Long', 'Forward', 'Unsucc Forward', 'Line Break',
           'Loss of Poss', 'Success', 'Unsuccess', 'Foul Won', 'PK Missed']

    selected_p90['minutes per 90'] = selected_p90['mins played']/90

    for column in per90:
        if column not in ['Goal', 'Assist', 'Yellow Card', 'Red Card', 'PK Missed', 'PK Scored']:
            selected_p90[column] = selected_p90[column] / selected_p90['minutes per 90']

    selected_p90 = selected_p90.drop(columns=['minutes per 90'])
    selected_p90.reset_index(drop=True, inplace=True)

    total_def_actions_columns = ['Tackle', 'Clear', 'Progr Inter', 'Unprogr Inter', 'Progr Rec', 
                             'Unprogr Rec', 'Stand. Tackle', 'Unsucc Stand. Tackle', 
                             'Unsucc Tackle']
    selected_p90['Total Def Actions'] = selected_p90[total_def_actions_columns].sum(axis=1)
    defending = selected_p90['Total Def Actions']

    adjustments = selected_p90[['Yellow Card', 'Red Card', 'Goal', 'Assist', 'PK Missed', 'PK Scored']]

    for index, row in adjustments.iterrows():
        if adjustments['PK Scored'][index] == 1:
            adjustments['Goal'][index] = adjustments['Goal'][index] - 1
        elif adjustments['PK Scored'][index] == 2:
            adjustments['Goal'][index] = adjustments['Goal'][index] - 2
    adjustments.fillna(0, inplace=True)
    adjustments['Yellow Card'] = adjustments['Yellow Card'] * -.2
    adjustments['Red Card'] = adjustments['Red Card'] * -2
    adjustments['Goal'] = adjustments['Goal'] * .9
    adjustments['Assist'] = adjustments['Assist'] * .6
    adjustments['PK Missed'] = adjustments['PK Missed'] * -1
    adjustments['PK Scored'] = adjustments['PK Scored'] * 0.6

    def calculate_percentile(value):
        return norm.cdf(value) * 100

    # Function to calculate z-score for each element in a column
    def calculate_zscore(column, mean, std):
        return (column - mean) / std

    def clip_percentile(value):
        return max(min(value, 85), 35)

    player_location = []
    for index, row in details.iterrows():
        if 'RW' == row['Position Tag'] or 'LW' == row['Position Tag']:
            player_location.append(index)       
    readding = []
    selected_p90 = pd.concat([details, selected_p90], axis=1)
    final = pd.DataFrame()


    for i in player_location:
        more_data = selected_p90.iloc[i]
        player_name = more_data['Player Full Name']
        team_name = more_data['Team Name']
        date = more_data['As At Date']
        
        if team_name in ['Boston Bolts U13', 'Boston Bolts U14']:
            wing_df = pd.read_csv("PostMatchReviewApp_v2/Thresholds/WingerThresholds1314.csv")
        elif team_name in ['Boston Bolts U15', 'Boston Bolts U16']:
            wing_df = pd.read_csv("PostMatchReviewApp_v2/Thresholds/WingerThresholds1516.csv")
        elif team_name in ['Boston Bolts U17', 'Boston Bolts U19']:
            wing_df = pd.read_csv("PostMatchReviewApp_v2/Thresholds/WingerThresholds1719.csv")

        mean_values = wing_df.iloc[0, 0]
        std_values = wing_df.iloc[1, 0]
        # Calculate the z-score for each data point
        z_scores_df = defending.transform(lambda col: calculate_zscore(col, mean_values, std_values))
        defending_percentile = z_scores_df.map(calculate_percentile)
        defending_percentile = defending_percentile.map(clip_percentile)
        defending_percentile = defending_percentile + 15
        will_defending = defending_percentile.iloc[player_location].reset_index()
        weights = np.array([.1])
        defending_score = (
            will_defending['Total Def Actions'] * weights[0]
            )

        add = adjustments.iloc[i, :].sum()
        readding.append(add)
        final_grade = (defending_score * .25)
        final['Defending'] = defending_score
        final['Final Grade'] = final_grade
        final['Player Name'] = player_name
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
