import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import VerticalPitch
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Circle
from FBGradeStreamlit import FBFunction
from CBGradeStreamlit import CBFunction
from CDMGradeStreamlit import CDMFunction
from CMGradeStreamlit import CMFunction
from WingerGradeStreamlit import WingerFunction
from StrikerGradeStreamlit import StrikerFunction
from GKGradeStreamlit import GKFunction
import matplotlib.image as mpimg
from MiddlePMRStreamlit import MiddlePMRStreamlit
from PIL import Image
from PositivesAndNegativesStreamlit import PositivesAndNegativesStreamlit
import glob
import os
import numpy as np
import matplotlib.patches as mpatches
from xGModel import xGModel
from AvgAttPositionOnField import AttackingPositionOnField
from AvgDefPositionOnField import DefendingPositionOnField
from GettingEventDataGrades import StrikerEventFunction, WingerEventFunction, CMEventFunction, DMEventFunction, FBEventFunction, CBEventFunction, GKEventFunction
from GettingTimeUntilRegain import formattingFileForRegain
from GettingPSDGradeData import getting_PSD_grade_data
import base64
from plotly_football_pitch import make_pitch_figure, PitchDimensions
import plotly_football_pitch as pfp
import plotly.graph_objs as go
import re
from streamlit_gsheets import GSheetsConnection
from GettingTopPlayers import getting_PSD_top_cat


# Setting a wide layout
st.set_page_config(layout='wide')

# adding in data from PMRApp
combined_df = st.session_state["combined_df"]
combined_df_copy = st.session_state['combined_df_copy']
selected_team = st.session_state["selected_team"]
selected_opp = st.session_state["selected_opp"]
selected_date = st.session_state["selected_date"]

# Getting player grade data and formatting it
player_data = getting_PSD_grade_data()
non_number_columns = ['Player Full Name', 'Team Name', 'Position Tag', 'Match Date', 'Opposition']
for col in player_data.columns:
    if col not in non_number_columns:
        player_data[col] = player_data[col].astype(float)
player_data['Match Date'] = pd.to_datetime(player_data['Match Date']).dt.strftime('%m/%d/%Y')
player_data.loc[player_data['Opposition'] == 'St Louis', 'Match Date'] = '12/09/2023'


player_data_copy = player_data.copy()
grouped = player_data_copy.groupby(['Player Full Name', 'Position Tag'])['mins played'].sum().reset_index()
    
# Find the position with the most minutes played for each player
idx = grouped.groupby('Player Full Name')['mins played'].idxmax()
prime_pos = grouped.loc[idx].reset_index(drop=True)
prime_pos.rename(columns={'Position Tag': 'Primary Position'}, inplace=True)

# getting the primary position
player_data_copy = pd.merge(player_data_copy, prime_pos[['Player Full Name', 'Primary Position']], on='Player Full Name', how='inner')
del player_data_copy['Position Tag']
player_data_copy = player_data_copy.groupby(['Player Full Name', 'Opposition', 'Match Date', 'Team Name', 'Primary Position'])[['mins played']].sum()
player_data_copy.reset_index(inplace=True)
player_data_copy['Match Identifier'] = player_data_copy['Team Name'] + ' vs ' + player_data_copy['Opposition'] + ' on ' + player_data_copy['Match Date'].astype(str)
match_identifiers = st.session_state['match_identifiers']
player_data_copy = player_data_copy[player_data_copy['Match Identifier'].isin(match_identifiers)]


# fromatting for the selected game
player_data = player_data.loc[(player_data['Team Name'] == selected_team) & (player_data['Opposition'] == selected_opp) & (player_data['Match Date'] == selected_date)]

# this gives us the total minutes played and shots for the whole team
# we will use this information to look at xT per 90 and xG per shot
total_mins_played = player_data['mins played'].sum()
total_shots = player_data['Efforts on Goal'].sum()
opp_shots = player_data['Opp Effort on Goal'].sum()
temp_shots = opp_shots.copy()
# if there is no opp efforts on goal, then we use other information
if opp_shots == 0:
    opp_shots = player_data[['Save Parried', 'Blocked Shot', 'Save Held', 'Goal Against']].sum()
    opp_shots = opp_shots.sum()

# getting the score
bolts_score = player_data['Goal'].astype(int).sum()
opp_score = player_data['Goal Against'].astype(int).sum()

if (selected_team == 'Boston Bolts U14 NALB' and 
    selected_opp == 'Seacoast of Bedford Seacoast United Bedford' and 
    selected_date == '09/21/2024'):
    opp_score += 1 

# getting the competition level from the Veo file
conn = st.connection('gsheets', type=GSheetsConnection)
comp_level = conn.read(worksheet='PMR', ttl=0)
comp_level = comp_level.loc[(comp_level['Bolts Team'] == selected_team) & (comp_level['Opposition'] == selected_opp) & (comp_level['Match Date'] == selected_date)]
comp_level.reset_index(drop=True, inplace=True)
url = comp_level.at[0, 'Veo Hyperlink']
comp_level = comp_level.at[0, 'Competition Level']

st.markdown(f"<h2 style='text-align: center;'>Bolts: {bolts_score}&nbsp;&nbsp;{selected_opp}: {opp_score}</h2>", unsafe_allow_html=True)
st.markdown(f"<h4 style='text-align: center;'>Date: {selected_date}&nbsp;&nbsp; Comp Level: {comp_level}</h4>", unsafe_allow_html=True)

# printing the three columns
col1, col2, col3 = st.columns(3)

folder_path = 'xG Input Files'

# Find all CSV files in the folder
csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

# List to hold individual DataFrames
df_list = []

# Loop through the CSV files and read them into DataFrames
for file in csv_files:
    df = pd.read_csv(file)
    df_list.append(df)

# Concatenate all DataFrames into a single DataFrame
fc_python = pd.concat(df_list, ignore_index=True)

# Making sure everything is aligned on one side
def flip_coordinates(x, y):
    # Flip x and y coordinates horizontally
    flipped_x = field_dim - x
    flipped_y = field_dim - y  # y remains unchanged in this transformation
    
    return flipped_x, flipped_y

field_dim = 100
# Iterating through coordinates and making them on one side
flipped_points = []
for index, row in fc_python.iterrows():
    if row['X'] < 50:
        flipped_x, flipped_y = flip_coordinates(row['X'], row['Y'])
        fc_python.at[index, 'X'] = flipped_x
        fc_python.at[index, 'Y'] = flipped_y


# Path to the folder containing CSV files
folder_path = 'Actions PSD'

# Find all CSV files in the folder
csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

# List to hold individual DataFrames
df_list = []

# Loop through the CSV files and read them into DataFrames
for file in csv_files:
    df = pd.read_csv(file)
    df.columns = df.loc[4]
    df = df.loc[5:].reset_index(drop=True)
    df_list.append(df)

# Concatenate all DataFrames into a single DataFrame
actions = pd.concat(df_list, ignore_index=True)
actions['Match Date'] = pd.to_datetime(actions['Match Date']).dt.strftime('%m/%d/%Y')
actions.loc[actions['Opposition'] == 'St Louis', 'Match Date'] = '12/09/2023'

# creating copies to work on
full_actions = actions.copy()
entire_actions = actions.copy()


full_actions = full_actions.loc[(full_actions['Team'] == selected_team) & (full_actions['Opposition'] == selected_opp) & (full_actions['Match Date'] == selected_date)].reset_index(drop=True)
full_actions_copy = full_actions.copy()
full_actions_copy2 = full_actions.copy()

# these are the ideal columns
cols = ['Player Full Name', 'Team', 'Match Date', 'Opposition', 'Action', 'Time', 'Video Link']
xg_actions = actions[cols]

# these are the shots we want
wanted_actions = ['Att Shot Blockd', 'Blocked Shot', 'Goal', 'Goal Against', 'Header on Target', 
                  'Header off Target', 'Opp Effort on Goal', 'Save Held', 'Save Parried', 'Shot off Target', 
                  'Shot on Target']
xg_actions = xg_actions.loc[xg_actions['Action'].isin(wanted_actions)].reset_index(drop=True)
# renaming for the join
xg_actions.rename(columns={'Team': 'Bolts Team'}, inplace=True)

# if the opponent shots are 0, we factor in blocked shots
# if they aren't 0, then we don't factor in blocked shots
if temp_shots != 0:
    xg_actions = xg_actions.loc[xg_actions['Action'] != 'Blocked Shot'].reset_index(drop=True)

# this is handeling duplicated PlayerStatData shots 
temp_df = pd.DataFrame(columns=xg_actions.columns)
prime_actions = ['Opp Effort on Goal', 'Shot on Target']
remove_indexes = []
for index in range(len(xg_actions) - 1):
    if xg_actions.loc[index, 'Time'] == xg_actions.loc[index+1, 'Time']:
        temp_df = pd.concat([temp_df, xg_actions.loc[[index]], xg_actions.loc[[index + 1]]], ignore_index=False)
        bye1 = temp_df.loc[temp_df['Action'].isin(prime_actions)]
        # these are the indexes we want to remove
        remove_indexes.extend(bye1.index)
        
    temp_df = pd.DataFrame(columns=xg_actions.columns)     

# this is a copy with the removed duplicated PSD shots
actions_new = xg_actions.copy()
actions_new = actions_new.drop(remove_indexes).reset_index(drop=True) 

fc_python['Match Date'] = pd.to_datetime(fc_python['Match Date']).dt.strftime('%m/%d/%Y')

# combining into xG dataframe we want
combined_xg = pd.merge(fc_python, actions_new, on=['Bolts Team', 'Match Date', 'Time'], how='inner')

# running the model on our dataframe
xg = xGModel(combined_xg)

# Getting the chances created, is this something that PSD will consistently have in actions tab??
chances_created = full_actions.loc[full_actions['Action'] == 'Chance Created']

# converting everything to seconds
def time_to_seconds(time_str):
        minutes, seconds = map(int, time_str.split(':'))
        return minutes + (seconds/60)
    
# Apply the function to the 'Time' column
chances_created['Time'] = chances_created['Time'].apply(time_to_seconds)

# creating a copy for later
xg_copy = xg.copy()


xg = xg.loc[(xg['Bolts Team'] == selected_team) & (xg['Opposition'] == selected_opp) & (xg['Match Date'] == selected_date)]


# getting Bolts info
our_wanted_actions = ['Att Shot Blockd',  'Goal', 'Header on Target', 
                  'Header off Target', 'Shot off Target', 'Shot on Target']
xg_us = xg_copy.loc[xg_copy['Action'].isin(our_wanted_actions)]

# combining chances created rows and shots rows and sorting by time
chances_created = pd.concat([chances_created, xg_us], ignore_index=True)
chances_created = chances_created.sort_values('Time', ascending=True).reset_index(drop=True)

# Initialize columns for pairing
chances_created['xA'] = None

# Keep track of the last "Chance Created" event
last_chance_idx = None

# this will check if there is an associated chances created with each shot
for idx, row in chances_created.iterrows():
    if row['Action'] == 'Chance Created':
        last_chance_idx = idx
    elif row['Action'] in our_wanted_actions and last_chance_idx is not None:
        chances_created.at[last_chance_idx, 'xA'] = row['xG']
        last_chance_idx = None


# final formatting of chances created
chances_created = chances_created[['Player Full Name', 'Team', 'Opposition', 'Match Date', 'xG', 'xA']]
# summing the xA and xG for each player
chances_created = chances_created.groupby(['Player Full Name', 'Team', 'Opposition', 'Match Date'])[['xG', 'xA']].sum()
chances_created.reset_index(inplace=True)


player_data_copy.rename(columns={'Team Name': 'Team'}, inplace=True)
chances_created = pd.merge(chances_created, player_data_copy[['Player Full Name', 'Team', 'Opposition', 'Match Date', 'mins played', 'Primary Position']], 
                           on=['Player Full Name', 'Team', 'Opposition', 'Match Date'], how='outer')

chances_created['xG + xA'] = chances_created['xG'] + chances_created['xA']
# converting this to p90
chances_created['xG + xA'] = (chances_created['xG + xA']/chances_created['mins played']) * 90

select_event_df = chances_created.loc[(chances_created['Team'] == selected_team) & (chances_created['Opposition'] == selected_opp) & (chances_created['Match Date'] == selected_date)]




our_columns = ['Final Grade', 'Player Name', 'Position', 'Adjustments']
final_grade_df = pd.DataFrame(columns=our_columns)

# would ideally like to combine this into one dataframe with the event data
# CAN WE CONCACATENATE THE EVENT DATA TO PLAYER_DATA
# will be tough because the structure is limited to the time limits for each position

for index, row in player_data.iterrows():
    if row['Position Tag'] == 'ATT': 
        temp_df = player_data.loc[[index]]
        end_att = StrikerFunction(temp_df)
        final_grade_df = pd.concat([final_grade_df, end_att], ignore_index=True)
    elif (row['Position Tag'] == 'RW') or (row['Position Tag'] == 'LW'):
        temp_df = player_data.loc[[index]]
        end_att = WingerFunction(temp_df)
        final_grade_df = pd.concat([final_grade_df, end_att], ignore_index=True)
    elif (row['Position Tag'] == 'CM') or (row['Position Tag'] == 'RM') or (row['Position Tag'] == 'LM') or (row['Position Tag'] == 'AM'):
        temp_df = player_data.loc[[index]]
        end_att = CMFunction(temp_df)
        final_grade_df = pd.concat([final_grade_df, end_att], ignore_index=True)
    elif (row['Position Tag'] == 'DM'):
        temp_df = player_data.loc[[index]]
        end_att = CDMFunction(temp_df)
        final_grade_df = pd.concat([final_grade_df, end_att], ignore_index=True)
    elif (row['Position Tag'] == 'RCB') or (row['Position Tag'] == 'LCB') or (row['Position Tag'] == 'CB'):
        temp_df = player_data.loc[[index]]
        end_att = CBFunction(temp_df)
        final_grade_df = pd.concat([final_grade_df, end_att], ignore_index=True)
    elif 'RB' in row['Position Tag'] or 'LB' in row['Position Tag'] or 'RWB' in row['Position Tag'] or 'LWB' in row['Position Tag'] or 'WingB' in row['Position Tag']:
        temp_df = player_data.loc[[index]]
        end_att = FBFunction(temp_df)
        final_grade_df = pd.concat([final_grade_df, end_att], ignore_index=True)
    elif row['Position Tag'] == 'GK':
        temp_df = player_data.loc[[index]]
        end_att = GKFunction(temp_df)
        final_grade_df = pd.concat([final_grade_df, end_att], ignore_index=True)


temp_group = final_grade_df.groupby('Player Name')



# adding the adjustments and getting the primary position
temp_df = pd.DataFrame(columns=['Player Name', 'Position', 'Final Grade', 'Adjustments'])
for player_name, group in temp_group:
    group.reset_index(drop=True, inplace=True)
    if (len(group) > 1):
        total_adj = group['Adjustments'].sum()
        if group['Started'].any():
            position = group.loc[group['Started'] == 1, 'Position'].values[0]
        else:
            max_minutes_row = group.loc[group['Minutes'].idxmax()]
            position = max_minutes_row['Position']
        if len(group) == 3:
            first_weight = group.loc[0, 'Minutes']/(group.loc[0, 'Minutes'] + group.loc[1, 'Minutes'] + group.loc[2, 'Minutes'])
            second_weight = group.loc[1, 'Minutes']/(group.loc[0, 'Minutes'] + group.loc[1, 'Minutes'] + group.loc[2, 'Minutes'])
            third_weight = group.loc[2, 'Minutes']/(group.loc[0, 'Minutes'] + group.loc[1, 'Minutes'] + group.loc[2, 'Minutes'])
            final_grade = (first_weight * group.loc[0, 'Final Grade']) + (second_weight * group.loc[1, 'Final Grade']) + (third_weight * group.loc[2, 'Final Grade'])
        elif len(group) == 2:
            first_weight = group.loc[0, 'Minutes']/(group.loc[0, 'Minutes'] + group.loc[1, 'Minutes'])
            second_weight = group.loc[1, 'Minutes']/(group.loc[0, 'Minutes'] + group.loc[1, 'Minutes'])
            final_grade = (first_weight * group.loc[0, 'Final Grade']) + (second_weight * group.loc[1, 'Final Grade'])
        update_row = {
            'Player Name': player_name,
            'Position': position,
            'Final Grade': final_grade,
            'Adjustments': total_adj
            }
        update_row = pd.DataFrame([update_row])
        temp_df = pd.concat([temp_df, update_row], ignore_index=True)
    else:
        update_row2 = group[['Player Name', 'Position', 'Final Grade', 'Adjustments']]
        temp_df = pd.concat([temp_df, update_row2], ignore_index=True)
    

final_grade_df = temp_df.copy()


chances_created.fillna(0, inplace=True)

# Short term fix because something is wrong with getting the positions of attackers

for index, row in final_grade_df.iterrows():
    if row['Position'] == 'ATT':
        temp_event_df = chances_created.loc[(chances_created['Primary Position'] == 'ATT')]
        wanted = ['xG + xA', 'Team']
        temp_event_df = temp_event_df[wanted]
        select_temp_df = select_event_df.loc[select_event_df['Player Full Name'] == row['Player Name']]
        select_temp_df = select_temp_df[wanted]
        select_temp_df = StrikerEventFunction(temp_event_df, select_temp_df)
        final_grade_df.at[index, 'Final Grade'] = row['Final Grade'] + ((select_temp_df.at[0, 'Finishing'])*.2)
    elif (row['Position'] == 'RW') or (row['Position'] == 'LW'):
        temp_event_df = chances_created.loc[(chances_created['Primary Position'] == 'LW') | (chances_created['Primary Position'] == 'RW')]
        wanted = ['xG + xA', 'Team']
        temp_event_df = temp_event_df[wanted]
        select_temp_df = select_event_df.loc[select_event_df['Player Full Name'] == row['Player Name']]
        select_temp_df = select_temp_df[wanted]
        select_temp_df = WingerEventFunction(temp_event_df, select_temp_df)
        final_grade_df.at[index, 'Final Grade'] = row['Final Grade'] + ((select_temp_df.at[0, 'Finishing'])*.2)
    elif (row['Position'] == 'CM') or (row['Position'] == 'RM') or (row['Position'] == 'LM') or (row['Position'] == 'AM'):
        temp_event_df = chances_created.loc[(chances_created['Primary Position'] == 'RM') | (chances_created['Primary Position'] == 'LM')
                                         | (chances_created['Primary Position'] == 'AM') | (chances_created['Primary Position'] == 'CM')]
        wanted = ['xG + xA', 'Team']
        temp_event_df = temp_event_df[wanted]
        select_temp_df = select_event_df.loc[select_event_df['Player Full Name'] == row['Player Name']]
        select_temp_df = select_temp_df[wanted]
        select_temp_df = CMEventFunction(temp_event_df, select_temp_df)
        final_grade_df.at[index, 'Final Grade'] = row['Final Grade'] + ((select_temp_df.at[0, 'Playmaking'])*.2)



final_grade_df['Final Grade'] = final_grade_df['Final Grade'] + final_grade_df['Adjustments']


final_grade_df = final_grade_df[['Player Name', 'Position', 'Final Grade']]
final_grade_df.rename(columns={'Player Name': 'Player Full Name', 'Position': 'Position Tag'}, inplace=True)
final_grade_df['Final Grade'] = round(final_grade_df['Final Grade'], 1)

combined_df = combined_df.sort_values(by='Starts', ascending=False)
combined_df = combined_df.drop_duplicates(subset='Player Full Name', keep='first')
del combined_df['Position Tag']
combined_df = pd.merge(combined_df, final_grade_df, on=['Player Full Name'])

combined_df.loc[combined_df['Player Full Name'] == 'Sy Perkins', 'Position Tag'] = 'GK'

combined_df['Final Grade'] = np.clip(combined_df['Final Grade'], 5.00, 9.70)
combined_df['Final Grade'] = combined_df['Final Grade'].astype(float)
combined_df['Final Grade'] = combined_df['Final Grade'].round(1)


subs = combined_df.loc[combined_df['Starts'] == 0]
combined_df = combined_df.loc[combined_df['Starts'] != 0]
combined_df_event = combined_df.copy()


st.write(combined_df)

grouped = combined_df.groupby('Position Tag')

# Draw the pitch
fig, ax = plt.subplots(figsize=(5, 5))
pitch = VerticalPitch(line_color='black', line_alpha=0.8)
pitch.draw(ax=ax)

# Example usage
field_dim = 100  # Width of the field

# formatting the lineup
for player_name, group in grouped:
    
    if group['Position Tag'].iloc[0] == 'ATT':
        position = combined_df.loc[combined_df['Position Tag'] == 'ATT'].reset_index()
        position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
        if (len(position) == 1):
            # striker
            circle = Circle((40, 100), 7, edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(40.5, 98, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
            ax.text(40, 102.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')
        elif (len(position) == 2):    
            # lcf
            circle = Circle((25, 100), 7, edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(25.5, 98, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
            ax.text(25, 102.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')

            # rcf
            circle = Circle((55, 100), 7, edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(55.5, 98, position['Final Grade'][1], color='black', size=9, ha='center', va='center')
            ax.text(55, 102.5, position['Player Full Name'][1], color='black', size=6, ha='center', va='center')
        elif (len(position) == 3):    
            # lcf
            circle = Circle((20, 100), 7, edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(20.5, 98, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
            ax.text(20, 102.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')

            # rcf
            circle = Circle((60, 100), 7, edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(60.5, 98, position['Final Grade'][1], color='black', size=9, ha='center', va='center')
            ax.text(60, 102.5, position['Player Full Name'][1], color='black', size=6, ha='center', va='center')

            # cf
            circle = Circle((40, 100), 7, edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(40.5, 98, position['Final Grade'][2], color='black', size=9, ha='center', va='center')
            ax.text(40, 102.5, position['Player Full Name'][2], color='black', size=6, ha='center', va='center')

    elif group['Position Tag'].iloc[0] == 'RW':
        position = combined_df.loc[combined_df['Position Tag'] == 'RW'].reset_index()
        position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
        # right winger
        circle = Circle((70, 92), 7, edgecolor='black', facecolor='#6bb2e2')
        ax.add_patch(circle)
        ax.text(70.5, 90, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
        ax.text(70, 94.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')

    elif group['Position Tag'].iloc[0] == 'LW':
        position = combined_df.loc[combined_df['Position Tag'] == 'LW'].reset_index()
        position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
        # left winger
        circle = Circle((8, 92), 7, edgecolor='black', facecolor='#6bb2e2')
        ax.add_patch(circle)
        ax.text(8.5, 90, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
        ax.text(8, 94.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')
       
    elif group['Position Tag'].iloc[0] == 'AM':
        position = combined_df.loc[combined_df['Position Tag'] == 'AM'].reset_index()
        position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
        # AM
        circle = Circle((40, 70), 7, edgecolor='black', facecolor='#6bb2e2')
        ax.add_patch(circle)
        ax.text(40.5, 68, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
        ax.text(40, 72.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')

    elif group['Position Tag'].iloc[0] == 'RM':
        position = combined_df.loc[combined_df['Position Tag'] == 'RM'].reset_index()
        position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
        # rcm
        circle = Circle((55, 65), 7, edgecolor='black', facecolor='#6bb2e2')
        ax.add_patch(circle)
        ax.text(55.5, 63, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
        ax.text(55, 67.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')
    elif group['Position Tag'].iloc[0] == 'LM':
        position = combined_df.loc[combined_df['Position Tag'] == 'LM'].reset_index()
        position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
        # lcm
        circle = Circle((25, 65), 7, edgecolor='black', facecolor='#6bb2e2')
        ax.add_patch(circle)
        ax.text(25.5, 63, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
        ax.text(25, 67.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')
    elif group['Position Tag'].iloc[0] == 'CM':
        position = combined_df.loc[combined_df['Position Tag'] == 'CM'].reset_index()
        position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
        if (len(position) == 2):
            # lcm
            circle = Circle((25, 65), 7, edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(25.5, 63, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
            ax.text(25, 67.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')
            # rcm
            circle = Circle((55, 65), 7, edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(55.5, 63, position['Final Grade'][1], color='black', size=9, ha='center', va='center')
            ax.text(55, 67.5, position['Player Full Name'][1], color='black', size=6, ha='center', va='center')
        elif (len(position) == 3):
            # lcm
            circle = Circle((20, 65), 7, edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(20.5, 63, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
            ax.text(20, 67.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')
            # rcm
            circle = Circle((60, 65), 7, edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(60.5, 63, position['Final Grade'][1], color='black', size=9, ha='center', va='center')
            ax.text(60, 67.5, position['Player Full Name'][1], color='black', size=6, ha='center', va='center')
            # cm
            circle = Circle((40, 65), 7, edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(40.5, 63, position['Final Grade'][2], color='black', size=9, ha='center', va='center')
            ax.text(40, 67.5, position['Player Full Name'][2], color='black', size=6, ha='center', va='center')

    elif group['Position Tag'].iloc[0] == 'DM':
        position = combined_df.loc[combined_df['Position Tag'] == 'DM'].reset_index()
        position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
        if (len(position) == 1):
            # cdm
            circle = Circle((40, 45), 7,  edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(40.5, 43, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
            ax.text(40, 47.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')
        elif (len(position) == 2):
            # lcm
            circle = Circle((20, 45), 7, edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(20.5, 43, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
            ax.text(20, 47.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')
            # rcm
            circle = Circle((60, 45), 7, edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(60.5, 43, position['Final Grade'][1], color='black', size=9, ha='center', va='center')
            ax.text(60, 47.5, position['Player Full Name'][1], color='black', size=6, ha='center', va='center')

    elif group['Position Tag'].iloc[0] == 'LB':
        position = combined_df.loc[combined_df['Position Tag'] == 'LB'].reset_index()
        position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
        # lb
        circle = Circle((7, 25), 7, edgecolor='black', facecolor='#6bb2e2')
        ax.add_patch(circle)
        ax.text(7.5, 23, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
        ax.text(7, 27.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')

    elif group['Position Tag'].iloc[0] == 'RB':
        position = combined_df.loc[combined_df['Position Tag'] == 'RB'].reset_index()
        position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
        # rb
        circle = Circle((73, 25), 7, edgecolor='black', facecolor='#6cb2e2')
        ax.add_patch(circle)
        ax.text(73.5, 23, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
        ax.text(73, 27.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')
        
    elif group['Position Tag'].iloc[0] == 'RWB':
        position = combined_df.loc[combined_df['Position Tag'] == 'RWB'].reset_index()
        position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
        # rwb
        circle = Circle((73, 50), 7, edgecolor='black', facecolor='#6cb2e2')
        ax.add_patch(circle)
        ax.text(73.5, 48, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
        ax.text(73, 52.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')
        
    elif group['Position Tag'].iloc[0] == 'LWB':
        position = combined_df.loc[combined_df['Position Tag'] == 'LWB'].reset_index()
        position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
        # lwb
        circle = Circle((7, 50), 7, edgecolor='black', facecolor='#6bb2e2')
        ax.add_patch(circle)
        ax.text(7.5, 48, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
        ax.text(7, 52.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')

    elif group['Position Tag'].iloc[0] == 'GK':
        position = combined_df.loc[combined_df['Position Tag'] == 'GK'].reset_index()
        position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
        # gk
        circle = Circle((40, 5), 7, edgecolor='black', facecolor='#6bb2e2')
        ax.add_patch(circle)
        ax.text(40.5, 3, 'N/A', color='black', size=9, ha='center', va='center')
        ax.text(40, 7.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')
    
    # Checking for back three
    back_three = combined_df.loc[combined_df['Position Tag'] == 'CB']
    if len(back_three) == 0:
        if (group['Position Tag'].iloc[0] == 'LCB'):
            position = combined_df.loc[combined_df['Position Tag'] == 'LCB'].reset_index()
            position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
            # lcb
            circle = Circle((25, 20), 7, edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(25.5, 18, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
            ax.text(25, 22.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')
    
        elif group['Position Tag'].iloc[0] == 'RCB':
            position = combined_df.loc[combined_df['Position Tag'] == 'RCB'].reset_index()
            position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
            # rcb
            circle = Circle((55, 20), 7, edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(55.5, 18, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
            ax.text(55, 22.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')
    elif len(back_three) == 1:
        if group['Position Tag'].iloc[0] == 'CB':
            position = combined_df.loc[combined_df['Position Tag'] == 'CB'].reset_index()
            position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
            # mcb
            circle = Circle((40, 25), 7,  edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(40.5, 23, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
            ax.text(40, 27.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')

        elif group['Position Tag'].iloc[0] == 'LCB':
            position = combined_df.loc[combined_df['Position Tag'] == 'LCB'].reset_index()
            position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
            # lcb
            circle = Circle((20, 25), 7, edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(20.5, 23, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
            ax.text(20, 27.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')

        elif group['Position Tag'].iloc[0] == 'RCB':
            position = combined_df.loc[combined_df['Position Tag'] == 'RCB'].reset_index()
            position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
            # rcb
            circle = Circle((60, 25), 7, edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(60.5, 23, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
            ax.text(60, 27.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')
    elif len(back_three) == 2:
        position = combined_df.loc[combined_df['Position Tag'] == 'CB'].reset_index()
        position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
        # lcb
        circle = Circle((25, 20), 7, edgecolor='black', facecolor='#6bb2e2')
        ax.add_patch(circle)
        ax.text(25.5, 18, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
        ax.text(25, 22.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')
        
        # rcb
        circle = Circle((55, 20), 7, edgecolor='black', facecolor='#6bb2e2')
        ax.add_patch(circle)
        ax.text(55.5, 18, position['Final Grade'][1], color='black', size=9, ha='center', va='center')
        ax.text(55, 22.5, position['Player Full Name'][1], color='black', size=6, ha='center', va='center')

subs_length = len(subs)
subs['Player Full Name'] = subs['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
ax.text(100, 120, 'Substitutes', color='black', size=12, ha='center', va='center')
for i in range(subs_length):
    if subs['Position Tag'].iloc[i] != 'GK':
        y_position = 120 - i * 8 if subs_length == 1 else 112 - i * 8
        ax.text(100, y_position, f"{subs['Player Full Name'].iloc[i]} - {subs['Final Grade'].iloc[i]}", color='black', size=7.5, ha='center', va='center')
    else:
        y_position = 120 - i * 8 if subs_length == 1 else 112 - i * 8
        ax.text(100, y_position, f"{subs['Player Full Name'].iloc[i]} - N/A", color='black', size=7.5, ha='center', va='center')

font_path = 'NewAmsterdam-Regular.ttf'
title_font = FontProperties(fname=font_path)

fig.text(
    0.51, .9,
    "Player Ratings",
    size=16,
    ha="center", fontproperties=title_font, color="black"
)

fig.set_facecolor('white')
plt.gca().set_facecolor('white')

with col1:
    st.pyplot(fig)

# getting the overall df with all teams, dates, and opposition
overall_df = st.session_state['overall_df']
overall_df = overall_df.loc[(overall_df['Team Name'] == selected_team) & (overall_df['Opposition'] != selected_opp) & (overall_df['Date'] != selected_date)]
# creating a unique opposition and date identifier
overall_df['Unique Opp and Date'] = overall_df['Opposition'] + ' (' + overall_df['Date'] + ')'
# sorting by date
overall_df.sort_values(by='Date', inplace=True)

closest_before = overall_df.loc[overall_df['Date'] < selected_date]
compare_opps = list(overall_df['Unique Opp and Date'].unique())

if not closest_before.empty:
    flag = 1
    closest_game = closest_before.iloc[-1]
    compare_opps.append('5 Game Rolling Avg')
    compare_opps.append('Seasonal Rolling Avg')
else:
    flag = 0
    
if flag == 1: 
    closest_game_index = compare_opps.index(closest_game['Unique Opp and Date'])
    with col3:
        compare_opp = st.selectbox('Choose the Comparison Game:', compare_opps, index=closest_game_index)
    
    xg_overall = xg_copy.copy()
    bolts_df = xg_overall[xg_overall['Team'].str.contains('Bolts')]
    opp_df = xg_overall[~xg_overall['Team'].str.contains('Bolts')]
    
    # Group by the desired columns and aggregate
    bolts_agg = bolts_df.groupby(['Bolts Team', 'Match Date', 'Opposition']).agg(
        Bolts_xG=('xG', 'sum'),
        Bolts_Count=('xG', 'size')
    ).reset_index()
    
    opp_agg = opp_df.groupby(['Bolts Team', 'Match Date', 'Opposition']).agg(
        Opp_xG=('xG', 'sum'),
        Opp_Count=('xG', 'size')
    ).reset_index()
    
    # Merge the aggregated data
    overall_xg = pd.merge(bolts_agg, opp_agg, on=['Bolts Team', 'Match Date', 'Opposition'], how='outer')
    overall_xg.rename(columns={'Bolts Team': 'Team'}, inplace=True)
    overall_xg['xG per Shot'] = overall_xg['Bolts_xG']/overall_xg['Bolts_Count']
    overall_xg['Opp xG per Shot'] = overall_xg['Opp_xG']/overall_xg['Opp_Count']
    overall_xg.drop(columns=['Bolts_xG', 'Bolts_Count', 'Opp_xG', 'Opp_Count'], inplace=True)
    
    
    combined_entire_df = overall_xg.copy()
    combined_entire_df['Unique Opp and Date'] = combined_entire_df['Opposition'] + ' (' + combined_entire_df['Match Date'] + ')'
    
    # getting the positives and negatives
    opposition = selected_opp
    our_team = selected_team
    our_date = selected_date
    temp_date = selected_date
    top3, low3 = PositivesAndNegativesStreamlit(team_select=our_team, opp_select=opposition, date_select=temp_date, comp_opp_select=compare_opp, further_df=combined_entire_df)

change = ['Goal Against', 'Shots on Target Against', 'Loss of Poss', 'Foul Conceded', 'Opp xG per Shot', 'Time Until Regain']
opposition = selected_opp
our_team = selected_team
our_date = selected_date

with col3:
    inner_columns = st.columns(3)

    with inner_columns[0]:
        if flag == 1:
            html_string = ( "<span style='font-family: Arial; font-size: 10pt; color: green; "
                "text-decoration: underline; text-decoration-color: green;'><b>Positives</b></span>")
            st.write(html_string, unsafe_allow_html=True)
            for index, cat in top3.items():
                if index in change:
                    cat = cat * -1
                player_html = f"<span style='color: green; font-size: 10pt;'>{index}</span> <span style='color: green; font-size: 10pt;'>{round(cat, 2)}</span>"
                st.write(player_html, unsafe_allow_html=True)
        if flag == 0:
            st.write('Not enough games to calculate positives.')
    with inner_columns[1]:
        image_path = "pages/Veo.jpg"  # Replace with the path to your image

        def load_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

        # Get the base64-encoded image
        image_base64 = load_image(image_path)

        # HTML and CSS for making the image a clickable link
        st.markdown(
        f"""
        <a href="{url}" target="_blank">
            <img src="data:image/jpeg;base64,{image_base64}" style="cursor: pointer; width: 100px;"/>  <!-- Adjust width as needed -->
        </a>
        <br><br>  <!-- Add two line breaks here -->
        """,
        unsafe_allow_html=True
        )
    with inner_columns[2]:
        if flag == 1:
            html_string = ( "<span style='font-family: Arial; font-size: 10pt; color: red; "
                "text-decoration: underline; text-decoration-color: red;'><b>Negatives</b></span>")
            st.write(html_string, unsafe_allow_html=True)
            for index, cat in low3.items():
                if index in change:
                    cat = cat * -1
                player_html = f"<span style='color: red; font-size: 10pt;'>{index}</span> <span style='color: red; font-size: 10pt'>{round(cat, 2)}</span>"
                st.write(player_html, unsafe_allow_html=True)
        if flag == 0:
            st.write('Not enough games to calculate negatives.')

# Getting the PSD data
player_data_narrow = getting_PSD_top_cat(selected_team, selected_opp, selected_date)
player_data_narrow[['Line Break', 'Pass Completion ', 'Stand. Tackle', 'Tackle', 'Dribble']] = player_data_narrow[['Line Break', 'Pass Completion ', 'Stand. Tackle', 'Tackle', 'Dribble']].astype(float)
player_data_narrow['Total Tackles'] = player_data_narrow['Stand. Tackle'] + player_data_narrow['Tackle']

player_data_narrow.drop(columns={'Stand. Tackle', 'Tackle'}, inplace=True)


top_tacklers = player_data_narrow.nlargest(3, 'Total Tackles')
top_pass = player_data_narrow.nlargest(3, 'Pass Completion ')
top_dribble = player_data_narrow.nlargest(3, 'Dribble')

with col3:
    inner_columns = st.columns(3)

    with inner_columns[0]:# Display the HTML string with different styles using unsafe_allow_html=True
        html_string = ( "<span style='font-family: Arial; font-size: 10pt; color: #355870; "
            "text-decoration: underline; text-decoration-color: #355870;'><b>Dribbles</b></span>")
        st.write(html_string, unsafe_allow_html=True)
        for index, row in top_dribble.iterrows():
            player_html = f"<span style='color: #355870; font-size: 10pt;'>{row['Player Full Name']}</span> <span style='color: green; font-size: 10pt;'>{round(row['Dribble'], 2)}</span>"
            st.write(player_html, unsafe_allow_html=True)

    with inner_columns[1]:# Display the HTML string with different styles using unsafe_allow_html=True
        html_string = ( "<span style='font-family: Arial; font-size: 10pt; color: #355870; "
            "text-decoration: underline; text-decoration-color: #355870;'><b>Pass %</b></span>")
        st.write(html_string, unsafe_allow_html=True)
        for idx, player in top_pass.iterrows():
            player_html = f"<span style='color: #355870; font-size: 10pt;'>{player['Player Full Name']}</span> <span style='color: green; font-size: 10pt;'>{player['Pass Completion ']}</span>"
            st.write(player_html, unsafe_allow_html=True)

    with inner_columns[2]:# Display the HTML string with different styles using unsafe_allow_html=True
        html_string = ( "<span style='font-family: Arial; font-size: 10pt; color: #355870; "
            "text-decoration: underline; text-decoration-color: #355870;'><b>Tackles</b></span>")
        st.write(html_string, unsafe_allow_html=True)
        for idx, player in top_tacklers.iterrows():
            player_html = f"<span style='color: #355870; font-size: 10pt;'>{player['Player Full Name']}</span> <span style='color: green; font-size: 10pt;'>{player['Total Tackles']}</span>"
            st.write(player_html, unsafe_allow_html=True)

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
pd_df['Total Distance'] = pd_df['total_distance_m'] * 0.001
pd_df['Max Speed'] = pd_df['max_speed_kph'] * 0.621371
pd_df['High Intensity Distance'] = pd_df['total_high_intensity_distance_m']

def rearrange_team_name(team_name):
    # Define age groups and leagues
    age_groups = ['U15', 'U16', 'U17', 'U19', 'U13', 'U14']
    leagues = ['MLS Next', 'NAL Boston', 'NAL South Shore']
    
    # Find age group in the team name
    for age in age_groups:
        if age in team_name:
            # Find the league part
            league_part = next((league for league in leagues if league in team_name), '')
            if league_part == 'NAL Boston':
                league_part = 'NALB'
            
            # Extract the rest of the team name
            rest_of_name = team_name.replace(age, '').replace('NAL Boston', '').replace(league_part, '').strip()
            
            
            # Construct the new team name
            return f"{rest_of_name} {age} {league_part}"
    
    # Return the original team name if no age group is found
    return team_name

# Apply the function to the 'team_name' column
pd_df['bolts team'] = pd_df['bolts team'].apply(rearrange_team_name)
pd_df = pd_df.loc[(pd_df['bolts team'] == selected_team) & (pd_df['start_time'] == selected_date)]

top_td = pd_df.nlargest(3, 'Total Distance')
top_hid = pd_df.nlargest(3, 'High Intensity Distance')
top_speed = pd_df.nlargest(3, 'Max Speed')

with col3:
    inner_columns = st.columns(3)

    with inner_columns[0]:# Display the HTML string with different styles using unsafe_allow_html=True
        html_string = ( "<span style='font-family: Arial; font-size: 10pt; color: #355870; "
            "text-decoration: underline; text-decoration-color: #355870;'><b>Total Distance</b></span>")
        st.write(html_string, unsafe_allow_html=True)
        for index, row in top_td.iterrows():
            player_html = f"<span style='color: #355870; font-size: 10pt;'>{row['athlete_name']}</span> <span style='color: green; font-size: 10pt;'>{round(row['Total Distance'], 2)}</span>"
            st.write(player_html, unsafe_allow_html=True)

    with inner_columns[1]:# Display the HTML string with different styles using unsafe_allow_html=True
        html_string = ( "<span style='font-family: Arial; font-size: 10pt; color: #355870; "
            "text-decoration: underline; text-decoration-color: #355870;'><b>High Intensity Distance</b></span>")
        st.write(html_string, unsafe_allow_html=True)
        for idx, player in top_hid.iterrows():
            player_html = f"<span style='color: #355870; font-size: 10pt;'>{player['athlete_name']}</span> <span style='color: green; font-size: 10pt;'>{round(player['High Intensity Distance'], 2)}</span>"
            st.write(player_html, unsafe_allow_html=True)

    with inner_columns[2]:# Display the HTML string with different styles using unsafe_allow_html=True
        html_string = ( "<span style='font-family: Arial; font-size: 10pt; color: #355870; "
            "text-decoration: underline; text-decoration-color: #355870;'><b>Max Speed</b></span>")
        st.write(html_string, unsafe_allow_html=True)
        for idx, player in top_speed.iterrows():
            player_html = f"<span style='color: #355870; font-size: 10pt;'>{player['athlete_name']}</span> <span style='color: green; font-size: 10pt;'>{round(player['Max Speed'], 2)}</span>"
            st.write(player_html, unsafe_allow_html=True)


team_sum = xg.groupby('Team')['xG'].sum()


bolts_xG = round(team_sum.loc[selected_team], 2)
opp_xG = round(team_sum.loc[selected_opp], 2)


bolts = xg.loc[xg['Team'].str.contains('Boston Bolts')]
opp = xg.loc[~xg['Team'].str.contains('Boston Bolts')]

bolts_mean = bolts['xG'].mean()
opp_mean = opp['xG'].mean()

bolts_player = bolts.groupby('Player Full Name')['xG'].sum()
max_xg_player = bolts_player.idxmax()

xg_data = xg.sort_values('Time').reset_index(drop=True)

a_xG = [0]
h_xG = [0]
a_min = [0]
h_min = [0]
hGoal_xG = []
aGoal_xG = []
aGoal_min = []
hGoal_min = []

# Finding the goal marks so that we can add those as points later on
for x in range(len(xg_data['xG'])):
    if "Goal" in xg_data['Event'][x] and xg_data['Team'][x] == selected_opp:
            aGoal_xG.append(xg_data['xG'][x])
            aGoal_min.append(xg_data['Time'][x])
    if xg_data['Event'][x] == "Goal" and xg_data['Team'][x]==selected_team:
            hGoal_xG.append(xg_data['xG'][x])
            hGoal_min.append(xg_data['Time'][x])
 
# Appending the xG value to the plot
for x in range(len(xg_data['xG'])):
    if xg_data['Team'][x]==selected_opp:
        a_xG.append(xg_data['xG'][x])
        a_min.append(xg_data['Time'][x])
    if xg_data['Team'][x]==selected_team:
        h_xG.append(xg_data['xG'][x])
        h_min.append(xg_data['Time'][x])
        
# sum all of the items in the list for xG
def nums_cumulative_sum(nums_list):
    return [sum(nums_list[:i+1]) for i in range(len(nums_list))]
a_cumulative = nums_cumulative_sum(a_xG)
h_cumulative = nums_cumulative_sum(h_xG)

# Rounding the total xGs
a_total = round(a_cumulative[-1],2)
h_total = round(h_cumulative[-1],2)

# This is for the end of the game
a_min.append(95)
h_min.append(95)
a_cumulative.append(a_total)
h_cumulative.append(h_total)

# Creating the plot
fig, ax = plt.subplots(figsize = (12,5))

# Adding the ticks to the plot
plt.xticks([0,15,30,45,60,75,90], size = 15)
plt.yticks(fontsize=15)

# Adding labels
plt.xlabel("Minute", size = 20)
plt.ylabel("xG", size = 20)
ax.xaxis.label.set_color('black')        #setting up X-axis label color to yellow
ax.yaxis.label.set_color('black')          #setting up Y-axis label color to blue

ax.tick_params(axis='x', colors='black')    #setting up X-axis tick color to red
ax.tick_params(axis='y', colors='black')  #setting up Y-axis tick color to black

# Setting up the different spines of the plot
ax.spines['left'].set_color('black')
ax.spines['bottom'].set_color('black')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False) 

# These are the dataframes that contain the minutes and xG
a_total = pd.DataFrame(zip(a_min, a_cumulative))
h_total = pd.DataFrame(zip(h_min, h_cumulative))
# These are the dataframes that take the minutes and the goals
aGoal_total = pd.DataFrame(zip(aGoal_min,aGoal_xG))
hGoal_total = pd.DataFrame(zip(hGoal_min,hGoal_xG))

# adding the goals into the line plot, if there are goals
for x in range(len(a_total[0])):
    # Checking for goals
    if len(aGoal_total) > 0:
        for y in range(len(aGoal_total[0])):
             if (a_total[0][x] == aGoal_total[0][y]):
                 aGoal_total[1][y] = a_total[1][x]
    else:
        continue
    
for x in range(len(h_total[0])):
    if len(hGoal_total) > 0:
        for y in range(len(hGoal_total[0])):
            if (h_total[0][x] == hGoal_total[0][y]):
                hGoal_total[1][y] = h_total[1][x]

# These are the line plots            
ax.plot(a_min, a_cumulative, color="black")
ax.plot(h_min, h_cumulative, color="#6bb2e2")
# These are the scatter plots
if len(aGoal_total) > 0:
    ax.scatter(aGoal_total[0], aGoal_total[1], color="black", s=90)
if len(hGoal_total) > 0:
    ax.scatter(hGoal_total[0], hGoal_total[1], color="#6bb2e2", s=90)
    
# Setting the background colors
fig.set_facecolor('white')
plt.gca().set_facecolor('white')


with col3: 
    st.markdown(
    """
    <div style='display: flex; flex-direction: column; align-items: center;'>
        <span style='font-family: Arial; font-size: 13pt; color: black;'><b>Expected Goals Time Series Chart</b></span>
        <div style='display: flex; justify-content: center;'>
            <span style='font-family: Arial; font-size: 10pt; color: #6bb2e2;'><b>Bolts xG: {bolts_xG}</b></span>
            <span>&nbsp;&nbsp;&nbsp;</span> <!-- Add spaces here -->
            <span style='font-family: Arial; font-size: 10pt; color: black;'><b>{selected_opp} xG: {opp_xG}</b></span>
        </div>
    </div>
    """.format(bolts_xG=bolts_xG, selected_opp=selected_opp, opp_xG=opp_xG),
    unsafe_allow_html=True
    )
    st.pyplot(fig)



game = player_data.copy()
combined_grades = pd.DataFrame()

og_columns = ['Player Full Name', 'Team Name', 'Position Tag',
              'mins played', 'Goal', 'Assist', 'Dribble', 'Goal Against',
              'Stand. Tackle', 'Unsucc Stand. Tackle', 'Tackle', 'Unsucc Tackle',
              'Def Aerial', 'Unsucc Def Aerial', 'Clear', 'Headed Clear',
              'Own Box Clear', 'Progr Rec', 'Unprogr Rec', 'Progr Inter',
              'Unprogr Inter', 'Progr Regain ', 'Blocked Shot', 'Blocked Cross',
              'Stand. Tackle Success ', 'Def Aerial Success ',
              'Att 1v1', 'Att Aerial', 'Efforts on Goal', 'Header on Target',
              'Header off Target', 'Shot on Target',
              'Att Shot Blockd', 'Cross', 'Unsucc Cross', 'Efficiency ', 'Side Back',
              'Unsucc Side Back', 'Long', 'Unsucc Long', 'Forward', 'Unsucc Forward',
              'Line Break', 'Pass into Oppo Box', 'Loss of Poss', 'Success',
              'Unsuccess', 'Pass Completion ', 'Progr Pass Attempt ',
              'Progr Pass Completion ', 'Foul Won', 'Foul Conceded', 'Yellow Card', 'Red Card']
number_columns = ['mins played', 'Goal', 'Assist', 'Dribble', 'Goal Against',
              'Stand. Tackle', 'Unsucc Stand. Tackle', 'Tackle', 'Unsucc Tackle',
              'Def Aerial', 'Unsucc Def Aerial', 'Clear', 'Headed Clear',
              'Own Box Clear', 'Progr Rec', 'Unprogr Rec', 'Progr Inter',
              'Unprogr Inter', 'Progr Regain ', 'Blocked Shot', 'Blocked Cross',
              'Stand. Tackle Success ', 'Def Aerial Success ',
              'Att 1v1', 'Att Aerial', 'Efforts on Goal', 'Header on Target',
              'Header off Target', 'Shot on Target',
              'Att Shot Blockd', 'Cross', 'Unsucc Cross', 'Efficiency ', 'Side Back',
              'Unsucc Side Back', 'Long', 'Unsucc Long', 'Forward', 'Unsucc Forward',
              'Line Break', 'Pass into Oppo Box', 'Loss of Poss', 'Success',
              'Unsuccess', 'Pass Completion ', 'Progr Pass Attempt ',
              'Progr Pass Completion ', 'Foul Won', 'Foul Conceded', 'Yellow Card', 'Red Card']
game = game[og_columns]
game[number_columns] = game[number_columns].astype(float)


def weighted_sum(group):
    total_minutes_played = group['mins played'].sum()
    return pd.Series({
        'Minutes Played': total_minutes_played,
        'Goal': group['Goal'].sum(),
        'Assist': group['Assist'].sum(),
        'Dribble': group['Dribble'].sum(),
        'Stand. Tackle': group['Stand. Tackle'].sum(),
        'Unsucc Stand. Tackle': group['Unsucc Stand. Tackle'].sum(),
        'Tackle': group['Tackle'].sum(),
        'Unsucc Tackle': group['Unsucc Tackle'].sum(),
        'Def Aerial': group['Def Aerial'].sum(),
        'Unsucc Def Aerial': group['Unsucc Def Aerial'].sum(),
        'Clear': group['Clear'].sum(),
        'Headed Clear': group['Headed Clear'].sum(),
        'Own Box Clear': group['Own Box Clear'].sum(),
        'Progr Rec': group['Progr Rec'].sum(),
        'Unprogr Rec': group['Unprogr Rec'].sum(),
        'Progr Inter': group['Progr Inter'].sum(),
        'Unprogr Inter': group['Unprogr Inter'].sum(),
        'Blocked Shot': group['Blocked Shot'].sum(),
        'Blocked Cross': group['Blocked Cross'].sum(),
        'Att 1v1': group['Att 1v1'].sum(),
        'Att Aerial': group['Att Aerial'].sum(),
        'Efforts on Goal': group['Efforts on Goal'].sum(),
        'Header on Target': group['Header on Target'].sum(),
        'Header off Target': group['Header off Target'].sum(),
        'Shot on Target': group['Shot on Target'].sum(),
        'Att Shot Blockd': group['Att Shot Blockd'].sum(),
        'Cross': group['Cross'].sum(),
        'Unsucc Cross': group['Unsucc Cross'].sum(),
        'Side Back': group['Side Back'].sum(),
        'Unsucc Side Back': group['Unsucc Side Back'].sum(),
        'Long': group['Long'].sum(),
        'Unsucc Long': group['Unsucc Long'].sum(),
        'Forward': group['Forward'].sum(),
        'Unsucc Forward': group['Unsucc Forward'].sum(),
        'Line Break': group['Line Break'].sum(),
        'Pass into Oppo Box': group['Pass into Oppo Box'].sum(),
        'Loss of Poss': group['Loss of Poss'].sum(),
        'Success': group['Success'].sum(),
        'Unsuccess': group['Unsuccess'].sum(),
        'Foul Won': group['Foul Won'].sum(),
        'Foul Conceded': group['Foul Conceded'].sum(),
        'Yellow Card': group['Yellow Card'].sum(),
        'Red Card': group['Red Card'].sum(),
        'Position': group['Position Tag'].iloc[0]
        })


game = game.groupby('Player Full Name').apply(weighted_sum).reset_index()
game['Progressive Regain %'] = ((game['Progr Rec'] + game['Progr Inter'])/(game['Progr Rec'] + game['Progr Inter'] + game['Unprogr Rec'] + game['Unprogr Inter'])) * 100 
game['Pass %'] = (game['Success']/(game['Success'] + game['Unsuccess'])) * 100


columns_to_sum = ['Goal', 'Assist', 'Dribble', 'Stand. Tackle', 'Tackle', 
                   'Def Aerial', 'Clear', 'Headed Clear', 'Own Box Clear', 'Progr Rec',
                   'Progr Inter', 'Blocked Shot', 'Blocked Cross', 'Att 1v1',
                   'Att Aerial', 'Efforts on Goal', 'Header on Target', 'Shot on Target',
                   'Att Shot Blockd', 'Cross', 'Side Back', 'Long', 
                   'Forward', 'Line Break', 'Pass into Oppo Box', 'Success',
                   'Foul Won']
game['Total Actions'] = game[columns_to_sum].sum(axis=1)


max_line_breaks = game['Line Break'].max()
max_dribbles = game['Dribble'].max()
max_regain = game['Progressive Regain %'].max()
max_pass_per = game['Pass %'].max()
max_totalActions = game['Total Actions'].max()



goalscorers = game[game['Goal'] >= 1]['Player Full Name'].tolist()
assists =  game[game['Assist'] >= 1]['Player Full Name'].tolist()
line_breaks =  game[game['Line Break'] == max_line_breaks]['Player Full Name'].tolist()
dribbler = game[game['Dribble'] == max_dribbles]['Player Full Name'].tolist()
regainer = game[game['Progressive Regain %'] == max_regain]['Player Full Name'].tolist()
efficient_passer = game[game['Pass %'] == max_pass_per]['Player Full Name'].tolist()
total_actioner = game[game['Total Actions'] == max_totalActions]['Player Full Name'].tolist()
yellow_card_rec = game[game['Yellow Card'] == 1]['Player Full Name'].tolist()
red_card_rec = game[game['Red Card'] == 1]['Player Full Name'].tolist()

combined_df_copy.reset_index(drop=True, inplace=True)
game.reset_index(drop=True, inplace=True)

combined_grades['Player'] = combined_df_copy['Player Full Name']
mins_played = game['Minutes Played']
combined_grades = pd.merge(combined_grades, game[['Player Full Name', 'Minutes Played']], left_on='Player', right_on='Player Full Name', how='inner')
combined_grades.drop(columns=['Player Full Name'], inplace=True)
combined_grades['Position'] = combined_df_copy['Position Tag']
combined_grades['Started'] = combined_df_copy['Starts']

combined_grades['Yellow Card'] = combined_grades['Player'].isin(yellow_card_rec).astype(int)
combined_grades['Red Card'] = combined_grades['Player'].isin(red_card_rec).astype(int)
combined_grades['IsGoalScorer'] = combined_grades['Player'].isin(goalscorers).astype(int)
combined_grades['IsAssister'] = combined_grades['Player'].isin(assists).astype(int)
combined_grades['IsLineBreaks'] = combined_grades['Player'].isin(line_breaks).astype(int)
combined_grades['IsDribbler'] = combined_grades['Player'].isin(dribbler).astype(int)
combined_grades['IsRegain'] = combined_grades['Player'].isin(regainer).astype(int)
combined_grades['IsEfficientPasser'] = combined_grades['Player'].isin(efficient_passer).astype(int)
combined_grades['IsTotalActioner'] = combined_grades['Player'].isin(total_actioner).astype(int)

combined_grades['Minutes Played'] = combined_grades['Minutes Played'].astype(int)

combined_grades.sort_values('Position', inplace=True)

# ADD TOP XG and MOST DISTANCE
combined_grades['IsMostxG'] = 0
player_name_to_change = max_xg_player
index_to_change = combined_grades.index[combined_grades['Player'] == player_name_to_change].tolist()[0]
combined_grades.loc[index_to_change, 'IsMostxG'] = 1

starters = combined_grades[combined_grades['Started'] == 1]
subs = combined_grades[combined_grades['Started'] == 0]

#position_order = {
#    'ATT': 1, 'Wing': 2, 'LW': 3, 'RW': 4, 'AM': 5,
#    'CM': 6, 'DM': 7, 'LWB': 8, 'RWB': 15, 'LB': 10,
#    'RB': 16, 'LCB': 12, 'CB': 13, 'RCB': 14, 'GK': 17, 'UNK': 18
#}

position_order = {
    'ATT': 15, 'Wing': 14, 'LW': 13, 'RW': 12, 'AM': 11,
    'CM': 10, 'DM': 9, 'LWB': 8, 'RWB': 3, 'LB': 7,
    'RB': 2, 'LCB': 6, 'CB': 5, 'RCB': 4, 'GK': 1, 'UNK': 18
}

# Apply to starters and subs
starters['Position_Order'] = starters['Position'].map(position_order)
starters['Position_Order'] = starters['Position_Order'].fillna(16)
starters_sorted = starters.sort_values(by='Position_Order', ascending=False).drop(columns='Position_Order').reset_index(drop=True)
subs['Position_Order'] = subs['Position'].map(position_order)
subs['Position_Order'] = subs['Position_Order'].fillna(16)
subs_sorted = subs.sort_values(by='Position_Order', ascending=False).drop(columns='Position_Order').reset_index(drop=True)

# Concatenate sorted DataFrames
combined_grades = pd.concat([subs_sorted, starters_sorted], ignore_index=True)


# changing long player names
for index, row in combined_grades.iterrows():
    if row['Player'] == 'Valentin Estevez Rubino':
        combined_grades.at[index, 'Player'] = 'Valentin Estevez-R'
    elif row['Player'] == 'Christian Martinez-Moule':
        combined_grades.at[index, 'Player'] = 'Christian M-M'
    elif row['Player'] == 'Bayron Morales-Vega':
        combined_grades.at[index, 'Player'] = 'Bayron M-V'

# STOPPED HERE

fig, ax = plt.subplots(figsize=(8,8))


ncols = 4
nrows = len(combined_grades)

# Length of the table horizontally, could increase if player leads in so many categories
ax.set_xlim(0, 17)
# length of the table vertically
ax.set_ylim(0, nrows + 0.5)

positions = [0.25, 5.5, 10, 13.5]
columns = ['Player', 'Minutes Played', 'Position', 'Leaders']

stored = []

add = 0

# Add table's main text and bar chart
for i in range(nrows):
    for j, column in enumerate(columns):
        if j == 0:
            ha = 'left'
        else:
            ha = 'center'
        if column == 'Player':
            text_label = combined_grades[column].iloc[i]
            weight = 'normal'
            ax.annotate(
                xy=(positions[j]-.15, i + .5),
                text=str(text_label),
                ha=ha,
                va='center',
                weight=weight, 
                fontsize = 12
            )
        elif column == 'Minutes Played':
            weight = 'normal'
            text_label = combined_grades[column].iloc[i]
            ax.annotate(
                xy=(positions[j]-.15, i + .5),
                text=str(text_label),
                ha=ha,
                va='center',
                weight=weight,
                fontsize=14
            )
        elif column == 'Position':
            weight = 'normal'
            text_label = combined_grades[column].iloc[i]
            ax.annotate(
                xy=(positions[j]-.19, i + .49),
                text=str(text_label),
                ha=ha,
                va='center',
                fontsize=14,
                weight=weight
            )
        else:
            if combined_grades['IsGoalScorer'][i] == 1:
                if i in stored:
                    add = 1
                else:
                    add = 0
                img = mpimg.imread('pages/IsGoalScorer.png')
                ax.imshow(img, extent=[positions[j] - 0.5,
                                     positions[j] + 0.5, i-.1, i + 1.1])
                stored.append(i)
                
            if combined_grades['IsDribbler'][i] == 1 and max_dribbles > 0:
                if i in stored:
                    add = 1
                else:
                    add = 0
                img = mpimg.imread('pages/IsDribbler.png')
                ax.imshow(img, extent=[positions[j] - 0.5 + add,
                                     positions[j] + 0.5 + add, i-.1, i + 1.1])
                stored.append(i)
            if combined_grades['IsLineBreaks'][i] == 1 and max_line_breaks > 0:
                if i in stored:
                    add = 1 + add
                else:
                    add = 0
                img = mpimg.imread('pages/IsLineBreaks.png')
                ax.imshow(img, extent=[positions[j] - 0.5 + add,
                                     positions[j] + 0.5 + add, i-.1, i + 1.0])
                stored.append(i)
            if combined_grades['IsRegain'][i] == 1 and max_regain > 0:
                if i in stored:
                    add = 1 + add
                else:
                    add = 0
                img = mpimg.imread('pages/IsRegain.png')
                ax.imshow(img, extent=[positions[j] - 0.5 + add,
                                     positions[j] + 0.5 + add, i-.1, i + 1.1])
                stored.append(i)
            if combined_grades['IsTotalActioner'][i] == 1:
                if i in stored:
                    add = 1 + add
                else:
                    add = 0
                img = mpimg.imread('pages/IsTotalActioner.png')
                ax.imshow(img, extent=[positions[j] - 0.5 + add,
                                     positions[j] + 0.5 + add, i-.1, i + 1.1])
                stored.append(i)
            if combined_grades['IsAssister'][i] == 1:
                if i in stored:
                    add = 1 + add
                else:
                    add = 0
                img = mpimg.imread('pages/IsAssister.png')
                ax.imshow(img, extent=[positions[j] - 0.5 + add,
                                     positions[j] + 0.5 + add, i-.1, i + 1.1])
                stored.append(i)
            if combined_grades['IsMostxG'][i] == 1:
                if i in stored:
                    add = 1 + add
                else:
                    add = 0
                img = mpimg.imread('pages/IsMostxG.png')
                ax.imshow(img, extent=[positions[j] - 0.5 + add,
                                     positions[j] + 0.5 + add, i-.1, i + 1.1])
                stored.append(i)   
            if combined_grades['Red Card'][i] == 1:
                if i in stored:
                    add = 1 + add
                else:
                    add = 0
                img = mpimg.imread('pages/Red_Card.png')
                ax.imshow(img, extent=[positions[j] - 0.4 + add,
                                     positions[j] + 0.4 + add, i+.05, i + .95])
                stored.append(i) 
            if combined_grades['Yellow Card'][i] == 1:
                if i in stored:
                    add = 1 + add
                else:
                    add = 0
                img = mpimg.imread('pages/Yellow_Card.png')
                ax.imshow(img, extent=[positions[j] - 0.5 + add,
                                     positions[j] + 0.5 + add, i-.1, i + 1.1])
                stored.append(i)
            
            
        if i < nrows - 1 and combined_grades['Started'][i] == 0 and combined_grades['Started'][i + 1] == 1:
            ax.axhline(y=i + 1.1, color='black', linestyle='--', linewidth=1.5, alpha=0.2)
        
# filling in everything
column_names = ['Player', 'Minutes Played', 'Position', 'Leaders']
for index, c in enumerate(column_names):
    if index == 0:
        ha = 'left'
    else:
        ha = 'center'
    ax.annotate(
        xy=(positions[index]-.15, nrows + .15),
        text=column_names[index],
        ha=ha,
        va='bottom',
        weight='bold', fontsize=15
    )

# Add dividing lines
ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], [nrows, nrows],
        lw=1.5, color='black', marker='', zorder=4)

fig.set_facecolor('white')
ax.set_axis_off()


with col1:
    st.pyplot(fig)

# plotting key
image = Image.open('pages/Key3.png')

with col1:
    st.image(image, use_column_width=True)

conn = st.connection('gsheets', type=GSheetsConnection)
temp_overall_df = conn.read(worksheet='PMR', ttl=0)


temp_overall_df = temp_overall_df.loc[(temp_overall_df['Bolts Team'] == selected_team) & (temp_overall_df['Opposition'] == selected_opp) & (temp_overall_df['Match Date'] == selected_date)]
temp_overall_df.reset_index(drop=True, inplace=True)
in_possession_goal = temp_overall_df['In Possession Goals'][0]
out_possession_goal = temp_overall_df['Out of Possession Goals'][0]


with col2:
    st.markdown(
        """
        <div style='display: block; text-align: center;'>
            <span style='font-family: Arial; font-size: 10pt; color: #6aa84f;'><b>IN POSSESSION: {in_possession_goal}</b></span><br>
            <span style='font-family: Arial; font-size: 10pt; color: #b45f06;'><b>OUT POSSESSION: {out_possession_goal}</b></span>
        </div>
        """.format(in_possession_goal=in_possession_goal, out_possession_goal=out_possession_goal),
        unsafe_allow_html=True
    )
    
    #inner_columns = st.columns(4)
    inner_columns = st.columns(2)

    #with inner_columns[0]:
    #    fig = plottingBarChart(total_shots, opp_shots, 'Shots')
    #    st.pyplot(fig)
    #with inner_columns[0]:
    #    fig = AttackingPositionOnField(details=combined_df_event, event_data=full_actions_copy2)
    #    st.pyplot(fig)
    #with inner_columns[1]:
    #    fig = DefendingPositionOnField(combined_df_event, full_actions_copy2)
    #    st.pyplot(fig)

# STOPPED HERE

with col2:
    time_of_poss, time_until_regain = formattingFileForRegain(full_actions)
    time_until_regain = (time_until_regain/total_mins_played) * 990
    fig2 = MiddlePMRStreamlit(team=our_team, opp=opposition, date=our_date, avg_bolts_xg=bolts_mean, avg_opp_xg=opp_mean, regain_time=time_until_regain)
    
    fig2.text(
        0.5, .95,
        "Team Ratings",
        size=23,
        ha="center", fontfamily='Arial', color="black"
    )
    st.pyplot(fig2)


xg_data = xg.copy()


custom_order = ['Shot', 'Blocked', 'SOT', 'SOT Far Post', 'SOT Inside Post', 'Goal', 'Goal Far Post', 'Goal Inside Post']
xg_data['Event'] = pd.Categorical(xg_data['Event'], categories=custom_order, ordered=True)
xg_data = xg_data.sort_values('Event')

bolts_xg_data = xg_data.loc[xg_data['Team'].str.contains('Boston Bolts')]

dimensions = PitchDimensions(pitch_length_metres=100, pitch_width_metres=100)
fig1 = pfp.make_pitch_figure(
    dimensions,
    figure_height_pixels=475,
    figure_width_pixels=475
)

custom_order = ['Shot', 'Blocked', 'SOT', 'SOT Far Post', 'SOT Inside Post', 'Goal', 'Goal Far Post', 'Goal Inside Post']
xg_data['Event'] = pd.Categorical(xg_data['Event'], categories=custom_order, ordered=True)
xg_data = xg_data.sort_values('Event')

bolts_xg_data = xg_data.loc[xg_data['Team'].str.contains('Boston Bolts')]


for index, row in bolts_xg_data.iterrows():
    x, y, xG = row['X'], 100-row['Y'], row['xG']
    hteam = row['Team']
    player_name = row['Player Full Name']
    url = row['Video Link']

    if row['Event'] == 'Goal':
        fig1.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers+text',
            marker=dict(
                size=(xG * 30) + 5,  # Adjusted for Plotly's scaling
                color='lightblue',
                symbol='circle'
            ),
            name='Goal',
            showlegend=False,
            hovertext=f"{player_name}<br>xG: {xG:.2f}",  # Add hover text
            hoverinfo="text"  # Display hover text
        ))
        fig1.add_annotation(
            x=x,
            y=y+3,
            text=f'<a href="{url}" target="_blank" style="color:lightblue;">Link</a>',
            showarrow=False,
            font=dict(color="lightblue"),
            align="center"
        ) 
    elif row['Event'] == 'SOT':
        fig1.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers',
            marker=dict(
                size=(xG * 30) + 5,
                color='white',
                line=dict(color='lightblue', width=3),
                symbol='circle'
            ),
            name='SOT',
            showlegend=False,
            hovertext=f"{player_name}<br>xG: {xG:.2f}",  # Add hover text
            hoverinfo="text"  # Display hover text
        ))
        fig1.add_annotation(
            x=x,
            y=y+3,
            text=f'<a href="{url}" target="_blank" style="color:lightblue;">Link</a>',
            showarrow=False,
            font=dict(color="lightblue"),
            align="center"
        ) 
    else:
        fig1.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers',
            marker=dict(
                size=(xG * 30) + 5,
                color='lightblue',
                symbol='circle-open'
            ),
            name='Shot',
            showlegend=False,
            hovertext=f"{player_name}<br>xG: {xG:.2f}",  # Add hover text
            hoverinfo="text"  # Display hover text
            ))
        fig1.add_annotation(
            x=x,
            y=y+3,
            text=f'<a href="{url}" target="_blank" style="color:lightblue;">Link</a>',
            showarrow=False,
            font=dict(color="white"),
            align="center"
        ) 
        
fig1.add_trace(go.Scatter(
    x=[None],  # Dummy data
    y=[None],
    mode='markers',
    marker=dict(
        size=10,
        color='lightblue',
        symbol='circle'
    ),
    name='Goal',
    visible='legendonly'
))

fig1.add_trace(go.Scatter(
    x=[None],  # Dummy data
    y=[None],
    mode='markers',
    marker=dict(
        size=10,
        color='white',
        line=dict(color='lightblue', width=3),
        symbol='circle'
    ),
    name='SOT',
    visible='legendonly'
))

fig1.add_trace(go.Scatter(
    x=[None],  # Dummy data
    y=[None],
    mode='markers',
    marker=dict(
        size=10,
        color='lightblue',
        symbol='circle-open'
    ),
    name='Shot',
    visible='legendonly',
))
        


custom_order = ['Shot', 'Blocked', 'SOT', 'SOT Far Post', 'SOT Inside Post', 'Goal', 'Goal Far Post', 'Goal Inside Post']
xg_data['Event'] = pd.Categorical(xg_data['Event'], categories=custom_order, ordered=True)
xg_data = xg_data.sort_values('Event')

opp_xg_data = xg_data.loc[~xg_data['Team'].str.contains('Boston Bolts')]


for index, row in opp_xg_data.iterrows():
    x, y, xG, url = 100-row['X'], row['Y'], row['xG'], row['Video Link']

    ateam = row['Team']
    our_string = row['Event']
    if 'Goal' in our_string:
        fig1.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers+text',
            marker=dict(
                size=(xG * 30) + 5,  # Adjusted for Plotly's scaling
                color='red',
                symbol='circle'
            ),
            name='Goal Against',
            showlegend=False,
            hovertext=f"xG: {xG:.2f}",  # Add hover text
            hoverinfo="text"  # Display hover text
        ))
        fig1.add_annotation(
            x=x,
            y=y+3,
            text=f'<a href="{url}" target="_blank" style="color:red;">Link</a>',
            showarrow=False,
            font=dict(color="white"),
            align="center"
        ) 
    elif 'SOT' in our_string:
        fig1.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers',
            marker=dict(
                size=(xG * 30) + 5,
                color='white',
                line=dict(color='red', width=3),
                symbol='circle'
            ),
            name='SOT Against',
            showlegend=False,
            hovertext=f"xG: {xG:.2f}",  # Add hover text
            hoverinfo="text"  # Display hover text
        ))
        fig1.add_annotation(
            x=x,
            y=y+3,
            text=f'<a href="{url}" target="_blank" style="color:red;">Link</a>',
            showarrow=False,
            font=dict(color="white"),
            align="center"
        ) 
    else:
        fig1.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers',
            marker=dict(
                size=(xG * 30) + 5,
                color='red',
                symbol='circle-open'
            ),
            name='Shot Against',
            showlegend=False,
            hovertext=f"xG: {xG:.2f}",  # Add hover text
            hoverinfo="text"  # Display hover text
            ))
        fig1.add_annotation(
            x=x,
            y=y+3,
            text=f'<a href="{url}" target="_blank" style="color:red;">Link</a>',
            showarrow=False,
            font=dict(color="white"),
            align="center"
        ) 
        
# Add custom legend entries
fig1.add_trace(go.Scatter(
    x=[None],  # Dummy data
    y=[None],
    mode='markers',
    marker=dict(
        size=5,
        color='red',
        symbol='circle'
    ),
    name='Goal Against',
    visible='legendonly'
))

fig1.add_trace(go.Scatter(
    x=[None],  # Dummy data
    y=[None],
    mode='markers',
    marker=dict(
        size=5,
        color='white',
        line=dict(color='red', width=3),
        symbol='circle'
    ),
    name='SOT Against',
    visible='legendonly'
))

fig1.add_trace(go.Scatter(
    x=[None],  # Dummy data
    y=[None],
    mode='markers',
    marker=dict(
        size=5,
        color='red',
        symbol='circle-open'
    ),
    name='Shot Against',
    visible='legendonly',
))

fig1.update_layout(
    legend=dict(
        font=dict(
            size=8  # Decrease font size for smaller legend text
        ),
        itemsizing='constant',  # Keep marker sizes constant in the legend
        traceorder='normal'  # Keep the order of traces as added
    )
)

fig1.add_annotation(
    text="Click the top right of chart to see the shots better",
    x=0.5,
    y=1.13,  # Adjust this value to position the subtitle correctly
    xref="paper",
    yref="paper",
    showarrow=False,
    font=dict(
        size=14,
        family="Arial",
        color="gray"
    )
)

fig1.add_annotation(
    text = f"{selected_team} and {selected_opp} xG Shot Chart",
    y= 1.17,  # Vertical position of the title, 0.95 places it near the top
    x= 0.5,   # Horizontal position of the title, 0.5 centers it
    xref="paper",
    yref="paper",
    showarrow=False,
    font= dict(
        size= 18,
        family= 'Arial',
        color= 'black'
    )
)

with col2:
    st.plotly_chart(fig1)

st.session_state["selected_team"] = selected_team
st.session_state["selected_opp"] = selected_opp
st.session_state['selected_date'] = selected_date
