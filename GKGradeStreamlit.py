import pandas as pd
import numpy as np
from scipy.stats import norm
from datetime import datetime
import streamlit as st


def GKFunction(dataframe):


    final = pd.DataFrame()
    final['Player Name'] = dataframe['Player Full Name']
    final['Position'] = dataframe['Position Tag']
    final['Final Grade'] = 0
    final['Adjustments'] = 0
    
    return final

def GKMoreDetailedFunction(dataframe):

    details = dataframe.loc[:, ['Player Full Name', 'Team Name', 'Position Tag', 'Match Date', 'Starts']]



    number_columns = ['mins played', 'Goal Against', 'Progr Regain ', 'Progr Rec', 'Unprogr Rec', 'Progr Inter', 'Unprogr Inter',
                    'Success', 'Unsuccess', 'Pass Completion ', 'Save Held', 'Save Parried', 'Successful Cross', 'Red Card', 'Opp Effort on Goal', 
                    'Progr Pass Completion ']
    selected = dataframe.loc[:, ~dataframe.columns.duplicated()]
    selected_p90 =  selected.loc[:, number_columns].astype(float)
    per90 = ['Goal Against', 'Success', 'Unsuccess', 'Save Held', 'Save Parried', 'Successful Cross', 'Opp Effort on Goal']

    selected_p90['minutes per 90'] = selected_p90['mins played']/90

    for column in per90:
        if column not in ['Goal', 'Assist', 'Shot on Target', 'Yellow Card', 'Red Card']:
            selected_p90[column] = selected_p90[column] / selected_p90['minutes per 90']
            
    selected_p90 = selected_p90.drop(columns=['minutes per 90'])
    selected_p90.reset_index(drop=True, inplace=True)
    selected_p90.fillna(0, inplace=True)


    attacking = selected_p90[['Pass Completion ', 'Progr Pass Completion ']]
    attacking.fillna(0, inplace=True)

    # TEMPORARY NOT USING
    defending_area = selected_p90[['Successful Cross']]
    defending_area.fillna(0, inplace=True)

    defending_goal = selected_p90[['Save Held', 'Save Parried', 'Goal Against']]
    defending_goal['Total Saves'] = defending_goal['Save Held'] + defending_goal['Save Parried']
    defending_goal['Save %'] = (defending_goal['Total Saves']/(defending_goal['Total Saves'] + defending_goal['Goal Against']))*100
    defending_goal['Save %'] = defending_goal['Save %'].astype(float)
    defending_goal.fillna(0, inplace=True)
    defending_goal = defending_goal.loc[:, ['Total Saves', 'Save %']]

    defending_space = selected_p90[['Progr Regain ']]
    defending_space.fillna(0, inplace=True)

    organization = selected_p90[['Save Held', 'Save Parried', 'Goal Against', 'Opp Effort on Goal']]
    organization['SOT Against'] = organization['Save Held'] + organization['Save Parried'] + organization['Goal Against']
    organization.fillna(0, inplace=True)
    organization = organization.loc[:, ['Opp Effort on Goal', 'SOT Against']]

    crosses = selected_p90[['Successful Cross', 'Unsucc cross GK']]
    crosses['Total CC'] = crosses['Successful Cross'] + crosses['Unsucc cross GK']
    crosses['Cross %'] = (crosses['Successful Cross']/crosses['Total CC'])*100
    crosses.fillna(0, inplace=True)
    crosses = crosses.loc[:, ['Cross %']]



    adjustments = pd.DataFrame()
    adjustments['Red Card'] = selected['Red Card']
    adjustments.fillna(0, inplace=True)
    adjustments['Red Card'] = adjustments['Red Card'] * -1

    adjustments['Playing Up'] = float(0)

    adjustments['Total Distance'] = float(0)

    team_data = {'Name': ['Jack Susi', 'Joao Almeida', 'Ben Marro', 'Casey Powers', 'Jack Seaborn', 'Aaron Choi', 'Ben Hanas'],
            'Team Name': ['Boston Bolts U13', 'Boston Bolts U14', 'Boston Bolts U15', 'Boston Bolts U16', 'Boston Bolts U15', 'Boston Bolts U17',
                        'Boston Bolts U19']}

    # Create a DataFrame
    team_df = pd.DataFrame(team_data)

    gk_details = details.loc[details['Position Tag'] == 'GK']

    avg_u13 = 2.8
    avg_u14 = 3.0
    avg_u15 = 3.4
    avg_u16 = 3.8
    avg_u17 = 4.0
    avg_u19 = 4.0

    # RECORDED DISTANCE
    total_dist = []

    for index2, row2 in gk_details.iterrows():    
        for index, row in team_df.iterrows():
            if row2['Player Full Name'] == row['Name']:
                if row2['Team Name'] == row['Team Name']:
                    adjustments['Playing Up'][index2] = 0
                else:
                    adjustments['Playing Up'][index2] = 1
                    
    c = 0

    if total_dist:
        for index2, row2 in gk_details.iterrows():
            # CHANGE TEAM NAME
            if 'U15' in row2['Team Name']:
                our_avg = avg_u15
                adjustments['Total Distance'][index2] = max(min(total_dist[c] - our_avg, 1), -1)
                c = c + 1
            elif 'U14' in row2['Team Name']:
                our_avg = avg_u14
                adjustments['Total Distance'][index2] = max(min(total_dist[c] - our_avg, 1), -1)
                c = c + 1
            elif 'U13' in row2['Team Name']:
                our_avg = avg_u13
                adjustments['Total Distance'][index2] = max(min(total_dist[c] - our_avg, 1), -1)
                c = c + 1
            elif 'U16' in row2['Team Name']:
                our_avg = avg_u16
                adjustments['Total Distance'][index2] = max(min(total_dist[c] - our_avg, 1), -1)
                c = c + 1
            elif 'U17' in row2['Team Name']:
                our_avg = avg_u17
                adjustments['Total Distance'][index2] = max(min(total_dist[c] - our_avg, 1), -1)
                c = c + 1
            elif 'U19' in row2['Team Name']:
                our_avg = avg_u19
                adjustments['Total Distance'][index2] = max(min(total_dist[c] - our_avg, 1), -1)
                c = c + 1



    def calculate_percentile(value):
        return norm.cdf(value) * 100

    # Function to calculate z-score for each element in a column
    def calculate_zscore(column, mean, std):
        return (column - mean) / std




    player_location = []
    # need to make this a list eventually
    for index, row in details.iterrows():
        if row['Position Tag'] == 'GK':
            player_location.append(index)  

        

    selected_p90 = pd.concat([details, selected_p90], axis=1)
    final = pd.DataFrame()
    readding = []

    total_def_actions = selected.loc[player_location, ['Progr Rec', 'Unprogr Rec', 'Progr Inter', 'Unprogr Inter']].astype(int).sum()
    total_def_actions = total_def_actions.sum()

    
    for i in player_location:
        more_data = selected_p90.iloc[i]
        player_name = selected_p90['Player Full Name'][i]
        team_name = more_data['Team Name']

        date = more_data['Match Date']

        gk_df = pd.read_csv("Thresholds/GoalkeeperThresholds.csv")
        
        if (total_def_actions != 0):
        
            mean_values = gk_df.iloc[0, [0, 6]]
            std_values = gk_df.iloc[1, [0, 6]]
            # Calculate the z-score for each data point
            z_scores_df = attacking.transform(lambda col: calculate_zscore(col, mean_values[col.name], std_values[col.name]))
            attacking_percentile = z_scores_df.map(calculate_percentile)
            player_attacking = attacking_percentile.iloc[player_location]
            weights = np.array([0.05, 0.05])
            attacking_score = (
                player_attacking['Pass Completion '] * weights[0] +
                player_attacking['Progr Pass Completion '] * weights[1]
                )
        
            # DOESN'T EXIST RIGHT NOW
            #weights = np.array([0.1])
            #defending_area_score = (
            #    ccp[index] * weights[0]
            #    )
        
        
            mean_values = gk_df.iloc[0, [2, 3]]
            std_values = gk_df.iloc[1, [2, 3]]
            # Calculate the z-score for each data point
            z_scores_df = defending_goal.transform(lambda col: calculate_zscore(col, mean_values[col.name], std_values[col.name]))
            defending_goal_percent = z_scores_df.map(calculate_percentile)
            defending_goal_player = defending_goal_percent.iloc[player_location]
            weights = np.array([.05, .05])
            defending_goal_score = (
                defending_goal_player['Total Saves'] * weights[0] +
                defending_goal_player['Save %'] * weights[1]
                )
        
            mean_values = gk_df.iloc[0, 4]
            std_values = gk_df.iloc[1, 4]
            # Calculate the z-score for each data point
            z_scores_df = defending_space.transform(lambda col: calculate_zscore(col, mean_values, std_values))
            defending_space_percent = z_scores_df.map(calculate_percentile)
            defending_space_player = defending_space_percent.iloc[player_location]
            weights = np.array([.1])
            defending_space_score = (
                defending_space_player['Progr Regain '] * weights[0]
                )
            
            mean_values = gk_df.iloc[0, [7, 8]]
            std_values = gk_df.iloc[1, [7, 8]]
            # Calculate the z-score for each data point
            z_scores_df = organization.transform(lambda col: calculate_zscore(col, mean_values[col.name], std_values[col.name]))
            organization_percent = z_scores_df.map(calculate_percentile)
            organization_percent = 100 - organization_percent
            organization_player = organization_percent.iloc[player_location]
            weights = np.array([.05, .05])
            organization_score = (
                organization_player['SOT Against'] * weights[0] +
                organization_player['Opp Effort on Goal'] * weights[1]
                )

            add = adjustments.iloc[i, :].sum()
            readding.append(add)
            
            final['Attacking'] = attacking_score
            #final['Defending Area'] = defending_area_score
            final['Defending Goal'] = defending_goal_score
            final['Defending Space'] = defending_space_score
            final['Organization'] = organization_score
            final['Final Grade'] = 0
            final['Team Name'] = team_name
            final['Date'] = date
            
        else:
            mean_values = gk_df.iloc[0, [0, 6]]
            std_values = gk_df.iloc[1, [0, 6]]
            # Calculate the z-score for each data point
            z_scores_df = attacking.transform(lambda col: calculate_zscore(col, mean_values[col.name], std_values[col.name]))
            attacking_percentile = z_scores_df.map(calculate_percentile)
            player_attacking = attacking_percentile.iloc[player_location]
            weights = np.array([0.05, 0.05])
            attacking_score = (
                player_attacking['Pass Completion '] * weights[0] +
                player_attacking['Progr Pass Completion '] * weights[1]
                )
        
            # DOESN'T EXIST RIGHT NOW
            #weights = np.array([0.1])
            #defending_area_score = (
            #    ccp[index] * weights[0]
            #    )
        
        
            mean_values = gk_df.iloc[0, [2, 3]]
            std_values = gk_df.iloc[1, [2, 3]]
            # Calculate the z-score for each data point
            z_scores_df = defending_goal.transform(lambda col: calculate_zscore(col, mean_values[col.name], std_values[col.name]))
            defending_goal_percent = z_scores_df.map(calculate_percentile)
            defending_goal_player = defending_goal_percent.iloc[player_location]
            weights = np.array([.05, .05])
            defending_goal_score = (
                defending_goal_player['Total Saves'] * weights[0] +
                defending_goal_player['Save %'] * weights[1]
                )
            
            mean_values = gk_df.iloc[0, [7, 8]]
            std_values = gk_df.iloc[1, [7, 8]]
            # Calculate the z-score for each data point
            z_scores_df = organization.transform(lambda col: calculate_zscore(col, mean_values[col.name], std_values[col.name]))
            organization_percent = z_scores_df.map(calculate_percentile)
            organization_percent = 100 - organization_percent
            organization_player = organization_percent.iloc[player_location]
            weights = np.array([.05, .05])
            organization_score = (
                organization_player['SOT Against'] * weights[0] +
                organization_player['Opp Effort on Goal'] * weights[1]
                )

            add = adjustments.iloc[i, :].sum()
            readding.append(add)
            
            final['Attacking'] = attacking_score
            #final['Defending Area'] = defending_area_score
            final['Defending Goal'] = defending_goal_score
            final['Defending Space'] = np.nan
            final['Organization'] = organization_score
            final['Final Grade'] = 0
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
                    
            
            
            
            
            
            
            
            
