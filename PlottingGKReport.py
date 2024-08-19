import plotly.graph_objs as go
import pandas as pd
import streamlit as st
from scipy.stats import norm
import numpy as np
from numpy.polynomial.polynomial import Polynomial

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
        showlegend=False  # Show the legend for the trendline
    ))

    # Line plot for the specified statistic over time
    for index, row in dataframe.iterrows():
        if row['Match Date'] == date_wanted:
            fig.add_trace(go.Scatter(
                x=[row['Match Date']],
                y=[row[statistic]],
                mode='markers',
                name='',
                marker=dict(color='lightblue', size=12, symbol='circle'),
                showlegend=False,  # Ensure no legend for this point
                text=row['More Opposition'] + ' (' + str(round(row[statistic], 4)) + ' )',  # Set hover text to Opposition
                hoverinfo='text'  # Display only the text (Opposition) in the hover tooltip
            ))
        else:    
            fig.add_trace(go.Scatter(
                x=[row['Match Date']],
                y=[row[statistic]],
                mode='lines+markers',
                name=f'{statistic} over time',
                line=dict(color='black'),
                marker=dict(color='black', size=6),
                showlegend=False,  # Remove legend
                text=row['More Opposition'] + ' (' + str(round(row[statistic], 4)) + ' )',  # Set hover text to Opposition
                hoverinfo='text'  # Display only the text (Opposition) in the hover tooltip
            ))



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

def gettingGameGrade(dataframe):
    gk_df = pd.read_csv("PostMatchReviewApp_v4/Thresholds/GoalkeeperThresholds.csv")
    dataframe.reset_index(drop=True, inplace=True)
    dataframe['Total Saves'] = dataframe['Save Held'] + dataframe['Save Parried']
    dataframe['SOT Against'] = dataframe['Save Held'] + dataframe['Save Parried'] + dataframe['Goal Against']

    final_dataframe = pd.DataFrame(columns=['Pass Completion ', 'Total Saves', 'Save %', 'Progr Regain ', 'SOT Against', 'Opp Effort on Goal',
                                            'GA-xGA', 'Progr Pass Completion '])

    raw_pass = dataframe.at[0, 'Pass Completion ']
    raw_pass = (raw_pass - gk_df.at[0, 'Pass Completion ']) / gk_df.at[1, 'Pass Completion ']
    raw_pass = norm.cdf(raw_pass) * 100
    final_dataframe.at[0, 'Pass Completion '] = raw_pass

    raw_progr_pass = dataframe.at[0, 'Progr Pass Completion ']
    raw_progr_pass = (raw_progr_pass - gk_df.at[0, 'Progr Pass Completion ']) / gk_df.at[1, 'Progr Pass Completion ']
    raw_progr_pass = norm.cdf(raw_progr_pass) * 100
    final_dataframe.at[0, 'Progr Pass Completion '] = raw_progr_pass

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


    if final_dataframe['Progr Regain '].isna().any():
        final_dataframe.at[0, 'Attacking'] = (final_dataframe.at[0, 'Pass Completion ']*0.06) + (final_dataframe.at[0, 'Progr Pass Completion ']*0.04)
        final_dataframe.at[0, 'Defending Goal'] = (final_dataframe.at[0, 'Total Saves']*.0125) + (final_dataframe.at[0, 'Save %']*0.0125) + (final_dataframe.at[0, 'GA-xGA']*.075)
        if final_dataframe['Opp Effort on Goal'].isna().any():
            final_dataframe.at[0, 'Organization'] = (final_dataframe.at[0, 'SOT Against']*.1)
        else:
            final_dataframe.at[0, 'Organization'] = (final_dataframe.at[0, 'SOT Against']*.05) + (final_dataframe.at[0, 'Opp Effort on Goal']*.05)
        final_dataframe.at[0, 'Final Grade'] = (final_dataframe.at[0, 'Attacking']*0.3)+(final_dataframe.at[0, 'Defending Goal']*0.5)+(final_dataframe.at[0, 'Organization']*.2)
    else:
        final_dataframe.at[0, 'Attacking'] = (final_dataframe.at[0, 'Pass Completion ']*0.06) + (final_dataframe.at[0, 'Progr Pass Completion ']*0.04)
        final_dataframe.at[0, 'Defending Goal'] = (final_dataframe.at[0, 'Total Saves']*.0125) + (final_dataframe.at[0, 'Save %']*0.0125) + (final_dataframe.at[0, 'GA-xGA']*.075)
        if final_dataframe['Opp Effort on Goal'].isna().any():
            final_dataframe.at[0, 'Organization'] = (final_dataframe.at[0, 'SOT Against']*.1)
        else:
            final_dataframe.at[0, 'Organization'] = (final_dataframe.at[0, 'SOT Against']*.05) + (final_dataframe.at[0, 'Opp Effort on Goal']*.05)
        final_dataframe.at[0, 'Defending Space'] = (final_dataframe.at[0, 'Progr Regain ']*.1)
        final_dataframe.at[0, 'Final Grade'] = (final_dataframe.at[0, 'Attacking']*0.2375)+(final_dataframe.at[0, 'Defending Goal']*0.4375)+(final_dataframe.at[0, 'Organization']*.1375)+(final_dataframe.at[0, 'Defending Space']*.1875)

    last_df = pd.DataFrame()
    last_df.at[0, 'Player Full Name'] = dataframe.at[0, 'Player Full Name']
    last_df.at[0, 'Match Date'] = dataframe.at[0, 'Match Date']
    last_df.at[0, 'Team'] = dataframe.at[0, 'Team']
    last_df.at[0, 'Opposition'] = dataframe.at[0, 'Opposition']
    last_df.at[0, 'Final Grade'] = final_dataframe.at[0, 'Final Grade']



    return last_df

def gkInvolvements(dataframe):
    in_poss = ['Success', 'Unsuccess']
    out_poss = ['Progr Rec', 'Progr Inter', 'Successful Cross']
    dataframe = dataframe[in_poss+out_poss].astype(int)
    in_possession = dataframe[in_poss].sum(axis=1).reset_index(drop=True)[0]
    out_of_possession = dataframe[out_poss].sum(axis=1).reset_index(drop=True)[0]
    return in_possession, out_of_possession