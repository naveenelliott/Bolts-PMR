import pandas as pd
import numpy as np
import streamlit as st
from GettingPSDTeamData import getting_PSD_team_data

def formatData(rows):
    kpi = ['Dribble', 'Goal Against',  'Progr Regain ', 'Total Corners', 'Shots on Target Against',
           'Total Cross', 'Total Forward', 'Att 1v1', 'Efforts on Goal', 'Shot on Target',
           'Efficiency ', 'Line Break', 'Pass into Oppo Box', 'xG per Shot', 'Opp xG per Shot',
           'Loss of Poss', 'Pass Completion ', 'Total Passes', 'Foul Conceded',
           'Progr Pass Attempt ', 'Progr Pass Completion ', 'Goal', 'Foul Won']
    game = rows.loc[:, kpi].astype(float)
    team_name = rows['Team']
    opp_name = rows['Opposition']
    game.insert(0, 'Team', team_name)
    game.insert(1, 'Opposition', opp_name)
    return game

def PositivesAndNegativesStreamlit(team_select, opp_select, date_select, comp_opp_select, further_df):
    if comp_opp_select != '5 Game Rolling Avg' and comp_opp_select != 'Seasonal Rolling Avg':
        overall = getting_PSD_team_data()
        # manually changing St Louis because weekly report and actions don't align
        overall.loc[overall['Opposition'] == 'St Louis', 'Date'] = '2023-12-09'
        overall['Date'] = pd.to_datetime(overall['Date']).dt.strftime('%m/%d/%Y')
        overall['Unique Opp and Date'] = overall['Opposition'] + ' (' + overall['Date'] + ')'
        overall.rename(columns={'Date': 'Match Date', 
                                   'Team Name': 'Team'}, inplace=True)
        first_game = overall.loc[(overall['Team'] == team_select) & (overall['Opposition'] == opp_select) 
                                & (overall['Match Date'] == date_select)]
        first_game_event = further_df.loc[(further_df['Team'] == team_select) & (further_df['Opposition'] == opp_select) 
                                & (further_df['Match Date'] == date_select)]
        first_game = pd.merge(first_game, first_game_event, on=['Team', 'Opposition', 'Match Date', 'Unique Opp and Date'], how='inner')
        closest_game = overall.loc[(overall['Team'] == team_select) & (overall['Unique Opp and Date'] == comp_opp_select)]
        closest_game_event = further_df.loc[(further_df['Team'] == team_select) & (further_df['Unique Opp and Date'] == comp_opp_select)]
        closest_game = pd.merge(closest_game, closest_game_event, on=['Team', 'Opposition', 'Match Date', 'Unique Opp and Date'], how='inner')

        first_game = formatData(first_game)
        second_game = formatData(closest_game)

        
        
        product = pd.concat([first_game, second_game], ignore_index=True)
        percent_change = (product.iloc[0, 2:] - product.iloc[1, 2:]) / product.iloc[1, 2:] * 100
        percent_change = percent_change.replace([np.inf, -np.inf], np.nan).dropna()
        columns_to_negate = ['Goal Against', 'Shots on Target Against', 'Loss of Poss', 'Foul Conceded', 'Opp xG per Shot', 'Time Until Regain']

        for column in columns_to_negate:
            if column in percent_change.index:
                percent_change[column] = percent_change[column] * -1
        
        top_three = percent_change.nlargest(3)
        low_three = percent_change.nsmallest(3)
        return top_three, low_three
    elif comp_opp_select == '5 Game Rolling Avg':
        overall = getting_PSD_team_data()
        # manually changing St Louis because weekly report and actions don't align
        overall.loc[overall['Opposition'] == 'St Louis', 'Date'] = '2023-12-09'
        overall['Date'] = pd.to_datetime(overall['Date']).dt.strftime('%m/%d/%Y')
        overall = overall.loc[overall['Team Name'] == team_select]
        overall = overall.sort_values('Date', ascending=True)
        overall.reset_index(inplace=True, drop=True)
        overall.rename(columns={'Date': 'Match Date', 
                                   'Team Name': 'Team'}, inplace=True)

        first_game = overall.loc[(overall['Team'] == team_select) & (overall['Opposition'] == opp_select) 
                                & (overall['Match Date'] == date_select)]
        st.write(first_game)
        first_game_event = further_df.loc[(further_df['Team'] == team_select) & (further_df['Opposition'] == opp_select) 
                                & (further_df['Match Date'] == date_select)]
        st.write(first_game_event)
        selected_game_idx = first_game.index[0]
        first_game = pd.merge(first_game, first_game_event, on=['Team', 'Opposition', 'Match Date'], how='inner')

        overall = pd.merge(overall, further_df, on=['Team', 'Opposition', 'Match Date'], how='outer')
        st.write(overall)

        # Get the last 10 games before the selected game
        rolling_games = overall.iloc[max(0, selected_game_idx - 5):selected_game_idx]

        # Calculate the weighted average
        rolling_games.drop(columns={'Team', 'Opposition', 'Match Date', 'Unique Opp and Date'}, inplace=True)
        rolling_games.reset_index(drop=True, inplace=True)
        if rolling_games['Opp Effort on Goal'].isnull().any():
            del rolling_games['Opp Effort on Goal']
            del first_game['Opp Effort on Goal']
        
        mean_avg = rolling_games.mean()
        mean_avg['Opposition'] = '5 Game Rolling Avg'
        
        first_game = formatData(first_game)

        # Create DataFrame from weighted average
        mean_avg = mean_avg.to_frame()
        mean_avg = mean_avg.T
        
        product = pd.concat([first_game, mean_avg], ignore_index=True)

        percent_change = (product.iloc[0, 2:] - product.iloc[1, 2:]) / product.iloc[1, 2:] * 100
        percent_change = percent_change.replace([np.inf, -np.inf], np.nan).dropna()
        columns_to_negate = ['Goal Against', 'Shots on Target Against', 'Loss of Poss', 'Foul Conceded', 'Opp xG per Shot', 'Time Until Regain']
        for column in columns_to_negate:
            if column in percent_change.index:
                percent_change[column] = percent_change[column] * -1
        top_three = percent_change.nlargest(3)
        low_three = percent_change.nsmallest(3)
        return top_three, low_three
    elif comp_opp_select == 'Seasonal Rolling Avg':
        overall = getting_PSD_team_data()
        # manually changing St Louis because weekly report and actions don't align
        overall.loc[overall['Opposition'] == 'St Louis', 'Date'] = '2023-12-09'
        overall['Date'] = pd.to_datetime(overall['Date']).dt.strftime('%m/%d/%Y')
        overall = overall.loc[overall['Team Name'] == team_select]
        overall = overall.sort_values('Date', ascending=True)
        overall.reset_index(inplace=True, drop=True)
        overall.rename(columns={'Date': 'Match Date', 
                                   'Team Name': 'Team'}, inplace=True)

        first_game = overall.loc[(overall['Team'] == team_select) & (overall['Opposition'] == opp_select) 
                                & (overall['Match Date'] == date_select)]
        first_game_event = further_df.loc[(further_df['Team'] == team_select) & (further_df['Opposition'] == opp_select) 
                                & (further_df['Match Date'] == date_select)]
        selected_game_idx = first_game.index[0]
        first_game = pd.merge(first_game, first_game_event, on=['Team', 'Opposition', 'Match Date'], how='inner')

        overall = pd.merge(overall, further_df, on=['Team', 'Opposition', 'Match Date'], how='outer')

        # Get the last 10 games before the selected game
        rolling_games = overall.iloc[:selected_game_idx]

        # Calculate the weighted average
        rolling_games.drop(columns={'Team', 'Opposition', 'Match Date', 'Unique Opp and Date'}, inplace=True)
        rolling_games.reset_index(drop=True, inplace=True)
        if rolling_games['Opp Effort on Goal'].isnull().any():
            del rolling_games['Opp Effort on Goal']
            del first_game['Opp Effort on Goal']
        
        mean_avg = rolling_games.mean()
        mean_avg['Opposition'] = 'Seasonal Rolling Avg'
        
        first_game = formatData(first_game)

        # Create DataFrame from weighted average
        mean_avg = mean_avg.to_frame()
        mean_avg = mean_avg.T
        
        product = pd.concat([first_game, mean_avg], ignore_index=True)

        percent_change = (product.iloc[0, 2:] - product.iloc[1, 2:]) / product.iloc[1, 2:] * 100
        percent_change = percent_change.replace([np.inf, -np.inf], np.nan).dropna()
        columns_to_negate = ['Goal Against', 'Shots on Target Against', 'Loss of Poss', 'Foul Conceded', 'Opp xG per Shot', 'Time Until Regain']
        for column in columns_to_negate:
            if column in percent_change.index:
                percent_change[column] = percent_change[column] * -1
        top_three = percent_change.nlargest(3)
        low_three = percent_change.nsmallest(3)
        return top_three, low_three

#top_three, low_three = PositivesAndNegativesStreamlit(team_select, opp_select, date_select)
