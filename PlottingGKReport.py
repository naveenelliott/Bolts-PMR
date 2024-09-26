import plotly.graph_objs as go
import pandas as pd
import streamlit as st
from scipy.stats import norm
import numpy as np
from numpy.polynomial.polynomial import Polynomial
import glob
import os

def plottingStatistics(dataframe, statistic, date_wanted):
    # Create the plot
    fig = go.Figure()

    dataframe['More Opposition'] = 'vs ' + dataframe['Opposition']
    dataframe['Match Date'] = pd.to_datetime(dataframe['Match Date']).dt.strftime('%m/%d/%Y')

    # Add the trendline to the plot
    fig.add_trace(go.Scatter(
        x=dataframe['Match Date'],
        y=dataframe[statistic],
        mode='lines',
        name='Trendline',
        line=dict(color='black', dash='dash'),
        showlegend=True  # Show the legend for the trendline
    ))

    current_game_shown = False
    # Line plot for the specified statistic over time
    for index, row in dataframe.iterrows():
        if row['Match Date'] == date_wanted:
            fig.add_trace(go.Scatter(
                x=[row['Match Date']],
                y=[row[statistic]],
                mode='markers',
                name='Current Game',
                marker=dict(color='lightblue', size=12, symbol='circle'),
                showlegend=True,  # Ensure no legend for this point
                text=row['More Opposition'] + ' (' + str(round(row[statistic], 4)) + ' )',  # Set hover text to Opposition
                hoverinfo='text'  # Display only the text (Opposition) in the hover tooltip
            ))
        else:    
            fig.add_trace(go.Scatter(
                x=[row['Match Date']],
                y=[row[statistic]],
                mode='lines+markers',
                name='Previous Games',
                line=dict(color='black'),
                marker=dict(color='black', size=6),
                showlegend=not current_game_shown,  # Remove legend
                text=row['More Opposition'] + ' (' + str(round(row[statistic], 4)) + ' )',  # Set hover text to Opposition
                hoverinfo='text'  # Display only the text (Opposition) in the hover tooltip
            ))
            current_game_shown = True



    # Customize the layout
    fig.update_layout(
        title=dict(
            text=f'{statistic} Over Time',
            x=0.5,  # Center the title
            xanchor='center',
            yanchor='top',
            font=dict(size=12)  # Smaller title font
        ),
        xaxis_title=dict(
            text='Match Date',
            font=dict(size=10)  # Smaller x-axis label font
        ),
        yaxis_title=dict(
            text=statistic,
            font=dict(size=10)  # Smaller y-axis label font
        ),
        xaxis=dict(
            showline=True, 
            showgrid=False, 
            showticklabels=True, 
            linecolor='gray',
            tickangle=45,  # Angle the x-axis ticks for better readability
            ticks='outside',  # Show ticks outside the plot
            tickcolor='black',
            tickfont=dict(
                size=9
            )
        ),
        yaxis=dict(
            showline=True, 
            showgrid=False, 
            showticklabels=True, 
            linecolor='gray',
            ticks='outside',
            tickcolor='black'
        ),
        font=dict(size=9)
    )

    # Display the plot in Streamlit
    return fig

def plottingInAndOut(dataframe, statistic1, statistic2, date_wanted):
    # Create the plot
    fig = go.Figure()

    dataframe['More Opposition'] = 'vs ' + dataframe['Opposition']
    dataframe['Match Date'] = pd.to_datetime(dataframe['Match Date']).dt.strftime('%m/%d/%Y')

    # Add the trendline to the plot
    fig.add_trace(go.Scatter(
        x=dataframe['Match Date'],
        y=dataframe[statistic1],
        mode='lines',
        name='Trendline\n(In Possession)',
        line=dict(color='black', dash='dash'),
        showlegend=True  # Show the legend for the trendline
    ))

    fig.add_trace(go.Scatter(
        x=dataframe['Match Date'],
        y=dataframe[statistic2],
        mode='lines',
        name='Trendline\n(Out Possession)',
        line=dict(color='gray', dash='dash'),
        showlegend=True  # Show the legend for the trendline
    ))

    # Line plot for the specified statistic over time
    
    current_game_shown = False
    for index, row in dataframe.iterrows():
        if row['Match Date'] == date_wanted:
            fig.add_trace(go.Scatter(
                x=[row['Match Date']],
                y=[row[statistic1]],
                mode='markers',
                name='Current Game\n(In Possession)',
                marker=dict(color='lightblue', size=12, symbol='circle'),
                showlegend=True,  # Ensure no legend for this point
                text=row['More Opposition'] + ' (' + str(round(row[statistic2], 4)) + ' )',  # Set hover text to Opposition
                hoverinfo='text'  # Display only the text (Opposition) in the hover tooltip
            ))
        else:    
            fig.add_trace(go.Scatter(
                x=[row['Match Date']],
                y=[row[statistic1]],
                mode='lines+markers',
                name='Previous Games\n(In Possession)',
                line=dict(color='black'),
                marker=dict(color='black', size=6),
                showlegend=not current_game_shown,  # Remove legend
                text=row['More Opposition'] + ' (' + str(round(row[statistic2], 4)) + ' )',  # Set hover text to Opposition
                hoverinfo='text'  # Display only the text (Opposition) in the hover tooltip
            ))
            current_game_shown = True

    for index, row in dataframe.iterrows():
        if row['Match Date'] == date_wanted:
            fig.add_trace(go.Scatter(
                x=[row['Match Date']],
                y=[row[statistic2]],
                mode='markers',
                name='Current Game\n(In Possession)',
                marker=dict(color='red', size=12, symbol='circle'),
                showlegend=True,  # Ensure no legend for this point
                text=row['More Opposition'] + ' (' + str(round(row[statistic1], 4)) + ' )',  # Set hover text to Opposition
                hoverinfo='text'  # Display only the text (Opposition) in the hover tooltip
            ))
        else:    
            fig.add_trace(go.Scatter(
                x=[row['Match Date']],
                y=[row[statistic2]],
                mode='lines+markers',
                name='Previous Games\n(In Possession)',
                line=dict(color='gray'),
                marker=dict(color='gray', size=6),
                showlegend=True,  # Remove legend
                text=row['More Opposition'] + ' (' + str(round(row[statistic1], 4)) + ' )',  # Set hover text to Opposition
                hoverinfo='text'  # Display only the text (Opposition) in the hover tooltip
            ))



    # Customize the layout
    fig.update_layout(
        title=dict(
            text=f'{statistic1} and {statistic2} Over Time',
            x=0.5,  # Center the title
            xanchor='center',
            yanchor='top',
            font=dict(size=12)  # Smaller title font
        ),
        xaxis_title=dict(
            text='Match Date',
            font=dict(size=10)  # Smaller x-axis label font
        ),
        yaxis_title=dict(
            text=f'{statistic1} and {statistic2}',
            font=dict(size=10)  # Smaller y-axis label font
        ),
        xaxis=dict(
            showline=True, 
            showgrid=False, 
            showticklabels=True, 
            linecolor='gray',
            tickangle=45,  # Angle the x-axis ticks for better readability
            ticks='outside',  # Show ticks outside the plot
            tickcolor='black',
            tickfont=dict(
                size=9
            )
        ),
        yaxis=dict(
            showline=True, 
            showgrid=False, 
            showticklabels=True, 
            linecolor='gray',
            ticks='outside',
            tickcolor='black'
        ),
        font=dict(size=9)
    )

    # Display the plot in Streamlit
    return fig

def gettingGameGrade(dataframe):
    gk_df = pd.read_csv("Thresholds/GoalkeeperThresholds.csv")
    dataframe.reset_index(drop=True, inplace=True)
    dataframe['Total Saves'] = dataframe['Save Held'] + dataframe['Save Parried']
    dataframe['SOT Against'] = dataframe['Save Held'] + dataframe['Save Parried'] + dataframe['Goal Against']

    mins_played = dataframe.at[0, 'mins played']
    
    
    final_dataframe = pd.DataFrame(columns=['Pass Completion ', 'Total Saves', 'Save %', 'Progr Regain ', 'SOT Against', 'Opp Effort on Goal',
                                            'GA-xGA', 'Progr Pass Completion ', 'Cross %'])

    raw_pass = dataframe.at[0, 'Pass Completion ']
    raw_pass = (raw_pass - gk_df.at[0, 'Pass Completion ']) / gk_df.at[1, 'Pass Completion ']
    raw_pass = norm.cdf(raw_pass) * 100
    final_dataframe.at[0, 'Pass Completion '] = raw_pass

    raw_progr_pass = dataframe.at[0, 'Progr Pass Completion ']
    raw_progr_pass = (raw_progr_pass - gk_df.at[0, 'Progr Pass Completion ']) / gk_df.at[1, 'Progr Pass Completion ']
    raw_progr_pass = norm.cdf(raw_progr_pass) * 100
    final_dataframe.at[0, 'Progr Pass Completion '] = raw_progr_pass

    #raw_throw = dataframe.at[0, 'Hand'

    raw_saves = dataframe.at[0, 'Total Saves']
    raw_saves = (raw_saves - gk_df.at[0, 'Total Saves']) / gk_df.at[1, 'Total Saves']
    raw_saves = norm.cdf(raw_saves) * 100
    raw_saves = 100 - raw_saves
    final_dataframe.at[0, 'Total Saves'] = raw_saves

    raw_save_per = dataframe.at[0, 'Save %']
    raw_save_per = (raw_save_per - gk_df.at[0, 'Save %']) / gk_df.at[1, 'Save %']
    raw_save_per = norm.cdf(raw_save_per) * 100
    final_dataframe.at[0, 'Save %'] = raw_save_per

    if pd.isna(dataframe.at[0, 'Progr Regain ']):
        raw_progr = np.nan
    else:
        raw_progr = dataframe.at[0, 'Progr Regain ']
        raw_progr = (raw_progr - gk_df.at[0, 'Progr Regain ']) / gk_df.at[1, 'Progr Regain ']
        raw_progr = norm.cdf(raw_progr) * 100
    final_dataframe.at[0, 'Progr Regain '] = raw_progr

    raw_sot_against = dataframe.at[0, 'SOT Against']
    raw_sot_against = (raw_sot_against - gk_df.at[0, 'SOT Against']) / gk_df.at[1, 'SOT Against']
    raw_sot_against = norm.cdf(raw_sot_against) * 100
    raw_sot_against = 100 - raw_sot_against
    final_dataframe.at[0, 'SOT Against'] = raw_sot_against

    if pd.isna(dataframe.at[0, 'Opp Effort on Goal']):
        raw_shots = np.nan
    else:
        raw_shots = dataframe.at[0, 'Opp Effort on Goal']
        raw_shots = (raw_shots - gk_df.at[0, 'Opp Effort on Goal']) / gk_df.at[1, 'Opp Effort on Goal']
        raw_shots = norm.cdf(raw_shots) * 100
    final_dataframe.at[0, 'Opp Effort on Goal'] = raw_shots

    raw_xga = dataframe.at[0, 'GA-xGA']
    raw_xga = (raw_xga - gk_df.at[0, 'Goals - xGA']) / gk_df.at[1, 'Goals - xGA']
    raw_xga = norm.cdf(raw_xga) * 100
    raw_xga = 100 - raw_xga
    final_dataframe.at[0, 'GA-xGA'] = raw_xga

    crosses = dataframe[['Successful Cross', 'Unsucc cross GK']]
    crosses['Total CC'] = crosses['Successful Cross'] + crosses['Unsucc cross GK']
    crosses['Cross %'] = (crosses['Successful Cross']/crosses['Total CC'])*100
    cross_claimed = crosses.at[0, 'Cross %'] * 0.1
    final_dataframe.at[0, 'Cross %'] = cross_claimed

    throws = dataframe[['Hands GK', 'Unsucc Hands']]
    throws['Totals Throw'] = throws['Hands GK'] + throws['Unsucc Hands']
    throws['Throw %'] = (throws['Hands GK']/throws['Totals Throw'])*100
    final_dataframe.at[0, 'Throw %'] = throws.at[0, 'Throw %']

    ground_gk = dataframe[['Ground GK', 'Unsucc Ground']]
    ground_gk['Total GKs'] = ground_gk['Ground GK'] + ground_gk['Unsucc Ground']
    ground_gk['Ground GK %'] = (ground_gk['Ground GK']/ground_gk['Total GKs'])*100
    final_dataframe.at[0, 'Goal Kick %'] = ground_gk.at[0, 'Ground GK %']

    if final_dataframe['Throw %'].notna().any():
        if final_dataframe['Goal Kick %'].notna().any():
            raw_gk = final_dataframe.at[0, 'Goal Kick %']
            gk_factor = (raw_gk - gk_df.at[0, 'Goal Kick %']) / gk_df.at[1, 'Goal Kick %']
            raw_throw = final_dataframe.at[0, 'Throw %']
            throw_factor = (raw_throw - gk_df.at[0, 'Throw %']) / gk_df.at[1, 'Throw %']
            pass_comp = .055
            forward_comp = 0.035
            throw = .005
            goal_kick = .005
        else:
            gk_factor = 0
            goal_kick = 0
            raw_throw = final_dataframe.at[0, 'Throw %']
            throw_factor = (raw_throw - gk_df.at[0, 'Throw %']) / gk_df.at[1, 'Throw %']
            pass_comp = .0567
            forward_comp = 0.0367
            throw = .0067
    else:
        if final_dataframe['Goal Kick %'].notna().any():
            raw_gk = final_dataframe.at[0, 'Goal Kick %']
            gk_factor = (raw_gk - gk_df.at[0, 'Goal Kick %']) / gk_df.at[1, 'Goal Kick %']
            pass_comp = .0567
            forward_comp = 0.0367
            goal_kick = .0067
            throw = 0
            throw_factor = 0
        else:
            gk_factor = 0
            pass_comp = .06
            forward_comp = 0.04
            goal_kick = 0
            throw = 0
            throw_factor = 0


    if final_dataframe['Progr Regain '].isna().any():
        final_dataframe.at[0, 'Attacking'] = (final_dataframe.at[0, 'Pass Completion ']*pass_comp) + (final_dataframe.at[0, 'Progr Pass Completion ']*forward_comp) + (throw_factor*throw) + (gk_factor*goal_kick)
        final_dataframe.at[0, 'Defending Goal'] = (final_dataframe.at[0, 'Total Saves']*.0125) + (final_dataframe.at[0, 'Save %']*0.0125) + (final_dataframe.at[0, 'GA-xGA']*.075)
        final_dataframe.at[0, 'Organization'] = (final_dataframe.at[0, 'SOT Against']*.05) + (final_dataframe.at[0, 'Opp Effort on Goal']*.05)
        if final_dataframe['Save %'].isna().any():
            if final_dataframe['Cross %'].isna().any():
                final_dataframe.at[0, 'Final Grade'] = (final_dataframe.at[0, 'Attacking']*0.55)+(final_dataframe.at[0, 'Organization']*.45)
            else:
                final_dataframe.at[0, 'Final Grade'] = (final_dataframe.at[0, 'Attacking']*0.3833)+(final_dataframe.at[0, 'Organization']*.2833)+(final_dataframe.at[0, 'Cross %']*.3333)
        else:
            if final_dataframe['Cross %'].isna().any():
                final_dataframe.at[0, 'Final Grade'] = (final_dataframe.at[0, 'Attacking']*0.3)+(final_dataframe.at[0, 'Defending Goal']*0.5)+(final_dataframe.at[0, 'Organization']*.2)
            else:
                final_dataframe.at[0, 'Final Grade'] = (final_dataframe.at[0, 'Attacking']*0.2375)+(final_dataframe.at[0, 'Defending Goal']*0.4375)+(final_dataframe.at[0, 'Organization']*.1375)+(final_dataframe.at[0, 'Cross %']*.1875)
    else:
        final_dataframe.at[0, 'Attacking'] = (final_dataframe.at[0, 'Pass Completion ']*pass_comp) + (final_dataframe.at[0, 'Progr Pass Completion ']*forward_comp) + (throw_factor*throw) + (gk_factor*goal_kick)
        final_dataframe.at[0, 'Defending Goal'] = (final_dataframe.at[0, 'Total Saves']*.0125) + (final_dataframe.at[0, 'Save %']*0.0125) + (final_dataframe.at[0, 'GA-xGA']*.075)
        final_dataframe.at[0, 'Organization'] = (final_dataframe.at[0, 'SOT Against']*.05) + (final_dataframe.at[0, 'Opp Effort on Goal']*.05)
        final_dataframe.at[0, 'Defending Space'] = (final_dataframe.at[0, 'Progr Regain ']*.1)
        if final_dataframe['Save %'].isna().any():
            if final_dataframe['Cross %'].isna().any():
                final_dataframe.at[0, 'Final Grade'] = (final_dataframe.at[0, 'Attacking']*0.3833)+(final_dataframe.at[0, 'Organization']*.2833)+(final_dataframe.at[0, 'Defending Space']*.3333)
            else:
                final_dataframe.at[0, 'Final Grade'] = (final_dataframe.at[0, 'Attacking']*0.3)+(final_dataframe.at[0, 'Cross %'] * .25)+(final_dataframe.at[0, 'Organization']*.2)+(final_dataframe.at[0, 'Defending Space']*.25)
        else:
            if final_dataframe['Cross %'].isna().any():
                final_dataframe.at[0, 'Final Grade'] = (final_dataframe.at[0, 'Attacking']*0.2375)+(final_dataframe.at[0, 'Defending Goal']*0.4375)+(final_dataframe.at[0, 'Organization']*.1375)+(final_dataframe.at[0, 'Defending Space']*.1875)
            else:
                final_dataframe.at[0, 'Final Grade'] = (final_dataframe.at[0, 'Attacking']*0.2)+(final_dataframe.at[0, 'Cross %'] * .15)+(final_dataframe.at[0, 'Defending Goal']*0.4)+(final_dataframe.at[0, 'Organization']*.1)+(final_dataframe.at[0, 'Defending Space']*.15)

    last_df = pd.DataFrame()
    last_df.at[0, 'Player Full Name'] = dataframe.at[0, 'Player Full Name']
    last_df.at[0, 'Match Date'] = dataframe.at[0, 'Match Date']
    last_df.at[0, 'Team'] = dataframe.at[0, 'Team']
    last_df.at[0, 'Opposition'] = dataframe.at[0, 'Opposition']
    last_df.at[0, 'Final Grade'] = final_dataframe.at[0, 'Final Grade']

    match_date = dataframe.at[0, 'Match Date']
    team = dataframe.at[0, 'Team']
    pname = dataframe.at[0, 'Player Full Name']

    # Path to the folder containing CSV files
    folder_path = 'PlayerData Files'
    
    # Find all CSV files in the folder
    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))
    
    # List to hold individual DataFrames
    df_list = []
    
    # Loop through the CSV files and read them into DataFrames
    for file in csv_files:
        df = pd.read_csv(file)
        df_list.append(df)
    
    # Concatenate all DataFrames into a single DataFrame
    pd_df = pd.concat(df_list, ignore_index=True)
    pd_df['start_time'] = pd.to_datetime(pd_df['start_time']).dt.strftime('%m/%d/%Y')
    pd_df['Total Distance'] = pd_df['total_distance_m'] * 0.000621371
    
    def rearrange_team_name(team_name):
        # Define age groups and leagues
        age_groups = ['U15', 'U16', 'U17', 'U19', 'U13', 'U14']
        leagues = ['MLS Next', 'NAL Boston', 'NAL South Shore']
        
        # Find age group in the team name
        for age in age_groups:
            if age in team_name:
                # Find the league part
                league_part = next((league for league in leagues if league in team_name), '')
                
                # Extract the rest of the team name
                rest_of_name = team_name.replace(age, '').replace(league_part, '').strip()
                
                # Construct the new team name
                return f"{rest_of_name} {age} {league_part}"
        
        # Return the original team name if no age group is found
        return team_name
    
    # Apply the function to the 'team_name' column
    pd_df['bolts team'] = pd_df['bolts team'].apply(rearrange_team_name)
    pd_df = pd_df.loc[(pd_df['bolts team'] == team) & (pd_df['start_time'] == match_date)]

    for index, row in pd_df.iterrows():
        if row['athlete_name'] == 'Benjamin Marro':
            pd_df.at[index, 'athlete_name'] = 'Ben Marro'
    
    pd_df = pd_df.loc[pd_df['athlete_name'] == pname].reset_index(drop=True)
    
    avg_u13 = 2.8
    avg_u14 = 3.0
    avg_u15 = 3.4
    avg_u16 = 3.8
    avg_u17 = 4.0
    avg_u19 = 4.0

    # RECORDED DISTANCE
    total_dist = np.nan


    adj = 0

    
    for index2, row2 in pd_df.iterrows():
        # CHANGE TEAM NAME
        if 'U15' in row2['bolts team']:
            our_avg = avg_u15
            total_dist = (pd_df.at[0, 'Total Distance']/mins_played) * 80
            adj = max(min(total_dist - our_avg, 1), -1)
        elif 'U14' in row2['bolts team']:
            our_avg = avg_u14
            total_dist = (pd_df.at[0, 'Total Distance']/mins_played) * 80
            adj = max(min(total_dist - our_avg, 1), -1)
        elif 'U13' in row2['bolts team']:
            our_avg = avg_u13
            total_dist = (pd_df.at[0, 'Total Distance']/mins_played) * 70
            adj = max(min(total_dist - our_avg, 1), -1)
        elif 'U16' in row2['bolts team']:
            our_avg = avg_u16
            total_dist = (pd_df.at[0, 'Total Distance']/mins_played) * 90
            adj = max(min(total_dist - our_avg, 1), -1)
        elif 'U17' in row2['bolts team']:
            our_avg = avg_u17
            total_dist = (pd_df.at[0, 'Total Distance']/mins_played) * 90
            adj = max(min(total_dist - our_avg, 1), -1)
        elif 'U19' in row2['bolts team']:
            our_avg = avg_u19
            total_dist = (pd_df.at[0, 'Total Distance']/mins_played) * 90
            adj = max(min(total_dist - our_avg, 1), -1)

    
    last_df.at[0, 'Final Grade'] = last_df.at[0, 'Final Grade'] + adj

    return last_df

def gkInvolvements(dataframe):
    in_poss = ['Success', 'Unsuccess']
    out_poss = ['Progr Rec', 'Progr Inter', 'Successful Cross']
    dataframe = dataframe[in_poss+out_poss].astype(int)
    in_possession = dataframe[in_poss].sum(axis=1).reset_index(drop=True)[0]
    out_of_possession = dataframe[out_poss].sum(axis=1).reset_index(drop=True)[0]
    return in_possession, out_of_possession
