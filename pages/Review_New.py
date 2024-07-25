import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import Pitch, VerticalPitch
from matplotlib.offsetbox import OffsetImage
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Circle
from highlight_text import fig_text
import numpy as np
from FBGradeStreamlit import FBFunction
from CBGradeStreamlit import CBFunction
from CDMGradeStreamlit import CDMFunction
from CMGradeStreamlit import CMFunction
from WingerGradeStreamlit import WingerFunction
from StrikerGradeStreamlit import StrikerFunction
from GKGradeStreamlit import GKFunction
from fuzzywuzzy import process
import matplotlib.image as mpimg
from MiddlePMRStreamlit import MiddlePMRStreamlit
from MiddlePMRStreamlit import GettingCompLevel
from PIL import Image
from PositivesAndNegativesStreamlit import PositivesAndNegativesStreamlit
from PositivesAndNegativesStreamlit import formatData
import glob
import os
import matplotlib.patches as mpatches
from xGModel import xGModel
from AvgAttPositionOnField import AttackingPositionOnField
from AvgDefPositionOnField import DefendingPositionOnField
import seaborn as sns
from ExpectedThreat import FindingExpectedThreat
from MeanStdExpectedThreat import MeanAndStdDev
from EventDataGradeStreamlit import averagesForEventData
from GettingEventDataGrades import StrikerEventFunction, WingerEventFunction, CMEventFunction, DMEventFunction, FBEventFunction, CBEventFunction
from GettingTimeUntilRegain import formattingFileForRegain
from GettingPSDGradeData import getting_PSD_grade_data



st.set_page_config(layout='wide')

combined_df = st.session_state["combined_df"]
combined_df_copy = st.session_state['combined_df_copy']
selected_team = st.session_state["selected_team"]
selected_opp = st.session_state["selected_opp"]
selected_date = st.session_state["selected_date"]

player_data = getting_PSD_grade_data()
non_number_columns = ['Player Full Name', 'Team Name', 'Position Tag', 'As At Date', 'Opposition']
for col in player_data.columns:
    if col not in non_number_columns:
        player_data[col] = player_data[col].astype(float)
player_data['As At Date'] = pd.to_datetime(player_data['As At Date'])
player_data['As At Date'] = player_data['As At Date'].dt.strftime('%m/%d/%Y')


player_data = player_data.loc[(player_data['Team Name'] == selected_team) & (player_data['Opposition'] == selected_opp) & (player_data['As At Date'] == selected_date)]


total_mins_played = player_data['mins played'].sum()
total_shots = player_data['Efforts on Goal'].sum()
# PLACEHOLDER
opp_shots = player_data['Opp Effort on Goal'].sum()
if opp_shots == 0:
    opp_shots = player_data[['Save Parried', 'Blocked Shot', 'Save Held', 'Goal Against']].sum()
    opp_shots = opp_shots.sum()


bolts_score = player_data['Goal'].astype(int).sum()
opp_score = player_data['Goal Against'].astype(int).sum()

comp_level = GettingCompLevel(selected_team, selected_opp, selected_date)

st.markdown(f"<h2 style='text-align: center;'>Bolts: {bolts_score}&nbsp;&nbsp;{selected_opp}: {opp_score}</h2>", unsafe_allow_html=True)
st.markdown(f"<h4 style='text-align: center;'>Date: {selected_date}&nbsp;&nbsp; Comp Level: {comp_level}</h4>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)


font_path = 'PermanentMarker-Regular.ttf'
permanent_marker_font = FontProperties(fname=font_path)
font_path = 'AccidentalPresidency.ttf'
title = FontProperties(fname=font_path)


#Draw the pitch
fig, ax = plt.subplots(figsize=(5, 5), dpi=600)
pitch = VerticalPitch(line_color='black', line_alpha=0.8)
pitch.draw(ax=ax)

our_columns = ['Final Grade', 'Player Name', 'Position', 'Adjustments']
final_grade_df = pd.DataFrame(columns=our_columns)

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

# Example usage
field_dim = 100  # Width of the field

def flip_coordinates(x, y):
    # Flip x and y coordinates horizontally
    flipped_x = field_dim - x
    flipped_y = field_dim - y  # y remains unchanged in this transformation
    
    return flipped_x, flipped_y


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

full_actions = actions.copy()
entire_actions = actions.copy()
full_actions = full_actions.loc[(full_actions['Team'] == selected_team) & (full_actions['Opposition'] == selected_opp)].reset_index(drop=True)

cols = ['Player Full Name', 'Team', 'Match Date', 'Opposition', 'Action', 'Time']
xg_actions = actions[cols]


wanted_actions = ['Att Shot Blockd', 'Blocked Shot', 'Goal', 'Goal Against', 'Header on Target', 
                  'Header off Target', 'Opp Effort on Goal', 'Save Held', 'Save Parried', 'Shot off Target', 
                  'Shot on Target']
xg_actions = xg_actions.loc[xg_actions['Action'].isin(wanted_actions)].reset_index(drop=True)
xg_actions.rename(columns={'Team': 'Bolts Team'}, inplace=True)
#actions = actions.loc[actions['Action'] != 'Blocked Shot'].reset_index(drop=True)
temp_df = pd.DataFrame(columns=xg_actions.columns)
prime_actions = ['Opp Effort on Goal', 'Shot on Target']
remove_indexes = []
for index in range(len(xg_actions) - 1):
    if xg_actions.loc[index, 'Time'] == xg_actions.loc[index+1, 'Time']:
        temp_df = pd.concat([temp_df, xg_actions.loc[[index]], xg_actions.loc[[index + 1]]], ignore_index=False)
        bye1 = temp_df.loc[temp_df['Action'].isin(prime_actions)]
        remove_indexes.extend(bye1.index)
        
    temp_df = pd.DataFrame(columns=xg_actions.columns)     
    
actions_new = xg_actions.copy()
actions_new = actions_new.drop(remove_indexes).reset_index(drop=True) 


combined_xg = pd.merge(actions_new, fc_python, left_index=True, right_index=True)
xg = xGModel(combined_xg)

chances_created = full_actions.loc[full_actions['Action'] == 'Chance Created']
def time_to_seconds(time_str):
        minutes, seconds = map(int, time_str.split(':'))
        return minutes + (seconds/60)
    
# Apply the function to the 'Time' column
chances_created['Time'] = chances_created['Time'].apply(time_to_seconds)

xg_copy = xg.copy()
xg = xg.loc[(xg['Bolts Team'] == selected_team) & (xg['Opposition'] == selected_opp)]
xg_later = xg.copy()

xg_us = xg_copy.loc[xg_copy['Bolts Team'] == selected_team]
our_wanted_actions = ['Att Shot Blockd', 'Blocked Shot', 'Goal', 'Header on Target', 
                  'Header off Target', 'Shot off Target', 'Shot on Target']
xg_us = xg_us.loc[xg_us['Action'].isin(our_wanted_actions)]

chances_created = pd.concat([chances_created, xg_us], ignore_index=True)
chances_created = chances_created.sort_values('Time', ascending=True).reset_index(drop=True)

# Initialize columns for pairing
chances_created['xA'] = None

# Keep track of the last "Chance Created" event
last_chance_idx = None

# Iterate through the DataFrame
for idx, row in chances_created.iterrows():
    if row['Action'] == 'Chance Created':
        last_chance_idx = idx
    elif row['Action'] in our_wanted_actions and last_chance_idx is not None:
        chances_created.at[last_chance_idx, 'xA'] = row['xG']
        last_chance_idx = None

chances_created = chances_created[['Player Full Name', 'Team', 'Opposition', 'Match Date', 'xG', 'xA']]
chances_created['Match Date'] = pd.to_datetime(chances_created['Match Date']).dt.strftime('%m/%d/%Y')
chances_created = chances_created.loc[chances_created['Team'].str.contains('Boston Bolts')]
chances_created = chances_created.groupby(['Player Full Name', 'Team', 'Opposition', 'Match Date'])[['xG', 'xA']].sum()
chances_created.reset_index(inplace=True)

all_event_df = averagesForEventData()

all_event_df = pd.merge(chances_created, all_event_df, on=['Player Full Name', 'Team', 'Opposition', 'Match Date'], how='outer')
all_event_df['xG + xA'] = all_event_df['xG'] + all_event_df['xA']
all_event_df['xG + xA'] = (all_event_df['xG + xA']/all_event_df['mins played']) * 90

select_event_df = all_event_df.loc[(all_event_df['Team'] == selected_team) & (all_event_df['Opposition'] == selected_opp)]


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

temp_df = pd.DataFrame(columns=['Player Name', 'Position', 'Final Grade', 'Adjustments'])
for player_name, group in temp_group:
    group.reset_index(drop=True, inplace=True)
    if (len(group) > 1):
        player_name = group.loc[0, 'Player Name']
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
        else:
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
# UPDATE FINAL GRADES HERE
for index, row in final_grade_df.iterrows():
    if row['Position'] == 'ATT':
        temp_event_df = all_event_df.loc[all_event_df['Primary Position'] == 'ATT']
        wanted = ['xG + xA', 'xT', 'Final Third Touches', 'Team']
        temp_event_df = temp_event_df[wanted]
        select_temp_df = select_event_df.loc[select_event_df['Player Full Name'] == row['Player Name']]
        select_temp_df = select_temp_df[wanted]
        select_temp_df = StrikerEventFunction(temp_event_df, select_temp_df)
        final_grade_df.at[index, 'Final Grade'] = row['Final Grade'] + ((select_temp_df.at[0, 'Passing'])*.2) + ((select_temp_df.at[0, 'Dribbling'])*.2) + ((select_temp_df.at[0, 'Finishing'])*.2)
    elif (row['Position'] == 'RW') or (row['Position'] == 'LW'):
        temp_event_df = all_event_df.loc[(all_event_df['Primary Position'] == 'LW') | (all_event_df['Primary Position'] == 'RW')]
        wanted = ['xG + xA', 'xT', 'Final Third Touches', 'Team']
        temp_event_df = temp_event_df[wanted]
        select_temp_df = select_event_df.loc[select_event_df['Player Full Name'] == row['Player Name']]
        select_temp_df = select_temp_df[wanted]
        select_temp_df = WingerEventFunction(temp_event_df, select_temp_df)
        final_grade_df.at[index, 'Final Grade'] = row['Final Grade'] + ((select_temp_df.at[0, 'Passing'])*.25) + ((select_temp_df.at[0, 'Dribbling'])*.25) + ((select_temp_df.at[0, 'Finishing'])*.25)
    elif (row['Position'] == 'CM') or (row['Position'] == 'RM') or (row['Position'] == 'LM') or (row['Position'] == 'AM'):
        temp_event_df = all_event_df.loc[(all_event_df['Primary Position'] == 'RM') | (all_event_df['Primary Position'] == 'LM')
                                         | (all_event_df['Primary Position'] == 'AM') | (all_event_df['Primary Position'] == 'CM')]
        wanted = ['xG + xA', 'xT', 'Team']
        temp_event_df = temp_event_df[wanted]
        select_temp_df = select_event_df.loc[select_event_df['Player Full Name'] == row['Player Name']]
        select_temp_df = select_temp_df[wanted]
        select_temp_df = CMEventFunction(temp_event_df, select_temp_df)
        final_grade_df.at[index, 'Final Grade'] = row['Final Grade'] + ((select_temp_df.at[0, 'Passing'])*.2) + ((select_temp_df.at[0, 'Playmaking'])*.2)
    elif (row['Position'] == 'DM'):
        temp_event_df = all_event_df.loc[(all_event_df['Primary Position'] == 'DM')]
        temp_event_df = temp_event_df[['xT', 'Team']]
        select_temp_df = select_event_df.loc[select_event_df['Player Full Name'] == row['Player Name']]
        select_temp_df = select_temp_df[['xT', 'Team']]
        select_temp_df = DMEventFunction(temp_event_df, select_temp_df)
        final_grade_df.at[index, 'Final Grade'] = row['Final Grade'] + ((select_temp_df.at[0, 'Passing'])*.2)
    elif (row['Position'] == 'RCB') or (row['Position'] == 'LCB') or (row['Position'] == 'CB'):
        temp_event_df = all_event_df.loc[(all_event_df['Primary Position'] == 'RCB') | (all_event_df['Primary Position'] == 'LCB') | (all_event_df['Primary Position'] == 'CB')]
        temp_event_df = temp_event_df[['xT', 'Team']]
        select_temp_df = select_event_df.loc[select_event_df['Player Full Name'] == row['Player Name']]
        select_temp_df = select_temp_df[['xT', 'Team']]
        select_temp_df = CBEventFunction(temp_event_df, select_temp_df)
        final_grade_df.at[index, 'Final Grade'] = row['Final Grade'] + ((select_temp_df.at[0, 'Passing'])*.2)
    elif 'RB' in row['Position'] or 'LB' in row['Position'] or 'RWB' in row['Position'] or 'LWB' in row['Position'] or 'WingB' in row['Position']:
        temp_event_df = all_event_df.loc[(all_event_df['Primary Position'] == 'RB') | (all_event_df['Primary Position'] == 'LB')
                                         | (all_event_df['Primary Position'] == 'RWB') | (all_event_df['Primary Position'] == 'LWB')
                                         | (all_event_df['Primary Position'] == 'WingB')]
        wanted = ['Final Third Passes', 'xT', 'Team']
        temp_event_df = temp_event_df[wanted]
        select_temp_df = select_event_df.loc[select_event_df['Player Full Name'] == row['Player Name']]
        select_temp_df = select_temp_df[wanted]
        select_temp_df = FBEventFunction(temp_event_df, select_temp_df)
        final_grade_df.at[index, 'Final Grade'] = row['Final Grade'] + ((select_temp_df.at[0, 'Passing'])*.2) + ((select_temp_df.at[0, 'Playmaking'])*.2)
    elif row['Position'] == 'GK':
        temp_event_df = all_event_df.loc[(all_event_df['Primary Position'] == 'GK')]
        temp_event_df = temp_event_df[['xT per Pass', 'Team']]
        select_temp_df = select_event_df.loc[select_event_df['Player Full Name'] == row['Player Name']]
        select_temp_df = select_temp_df[['xT per Pass', 'Team']]


final_grade_df['Final Grade'] = final_grade_df['Final Grade'] + final_grade_df['Adjustments']

final_grade_df = final_grade_df[['Player Name', 'Position', 'Final Grade']]
final_grade_df.rename(columns={'Player Name': 'Player Full Name', 'Position': 'Position Tag'}, inplace=True)
final_grade_df['Final Grade'] = round(final_grade_df['Final Grade'], 1)

combined_df = combined_df.sort_values(by='Starts', ascending=False)
combined_df = combined_df.drop_duplicates(subset='Player Full Name', keep='first')
del combined_df['Position Tag']
combined_df = pd.merge(combined_df, final_grade_df, on=['Player Full Name'])
for index, row in combined_df.iterrows():
    if row['Final Grade'] > 10.00:
        combined_df.at[index, 'Final Grade'] = 10.00
    elif row['Final Grade'] < 5.00:
        combined_df.at[index, 'Final Grade'] = 5.00

subs = combined_df.loc[combined_df['Starts'] == 0]
combined_df = combined_df.loc[combined_df['Starts'] != 0]

grouped = combined_df.groupby('Position Tag')

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
        elif (len(position) > 1):    
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
            ax.text(55.5, 63, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
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
        if group['Position Tag'].iloc[0] == 'LCB':
            position = combined_df.loc[combined_df['Position Tag'] == 'LCB'].reset_index()
            position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
            # lcb
            circle = Circle((25, 20), 7, edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(25.5, 18, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
            ax.text(25, 22.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')
    
        if group['Position Tag'].iloc[0] == 'RCB':
            position = combined_df.loc[combined_df['Position Tag'] == 'RCB'].reset_index()
            position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
            # rcb
            circle = Circle((55, 20), 7, edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(55.5, 18, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
            ax.text(55, 22.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')
    else:
        if group['Position Tag'].iloc[0] == 'CB':
            position = combined_df.loc[combined_df['Position Tag'] == 'CB'].reset_index()
            position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
            # mcb
            circle = Circle((40, 25), 7,  edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(40.5, 23, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
            ax.text(40, 27.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')

        if group['Position Tag'].iloc[0] == 'LCB':
            position = combined_df.loc[combined_df['Position Tag'] == 'LCB'].reset_index()
            position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
            # lcb
            circle = Circle((20, 25), 7, edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(20.5, 23, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
            ax.text(20, 27.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')

        if group['Position Tag'].iloc[0] == 'RCB':
            position = combined_df.loc[combined_df['Position Tag'] == 'RCB'].reset_index()
            position['Player Full Name'] = position['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
            # rcb
            circle = Circle((60, 25), 7, edgecolor='black', facecolor='#6bb2e2')
            ax.add_patch(circle)
            ax.text(60.5, 23, position['Final Grade'][0], color='black', size=9, ha='center', va='center')
            ax.text(60, 27.5, position['Player Full Name'][0], color='black', size=6, ha='center', va='center')


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

fig.set_facecolor('white')
plt.gca().set_facecolor('white')
fig.set_dpi(600)


with col1:
    st.pyplot(fig)

overall_df = st.session_state['overall_df']
overall_df.loc[overall_df['Opposition'] == 'St Louis', 'Date'] = '12/08/2023'
overall_df = overall_df.loc[overall_df['Team Name'] == selected_team]
overall_df = overall_df.loc[(overall_df['Opposition'] != selected_opp) & (overall_df['Date'] != selected_date)]
overall_df['Unique Opp and Date'] = overall_df['Opposition'] + ' (' + overall_df['Date'] + ')'
overall_df.sort_values(by='Date', inplace=True)

closest_before = overall_df.loc[overall_df['Date'] < selected_date]
closest_after = overall_df.loc[overall_df['Date'] > selected_date]
compare_opps = list(overall_df['Unique Opp and Date'].unique())

if not closest_before.empty:
    closest_game = closest_before.iloc[-1]
    compare_opps.append('10 Game Rolling Avg')
else:
    closest_game = closest_after.iloc[0]


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
overall_xg['Match Date'] = pd.to_datetime(overall_xg['Match Date']).dt.strftime('%m/%d/%Y')
overall_xg['xG per Shot'] = overall_xg['Bolts_xG']/overall_xg['Bolts_Count']
overall_xg['Opp xG per Shot'] = overall_xg['Opp_xG']/overall_xg['Opp_Count']
overall_xg.drop(columns=['Bolts_xG', 'Bolts_Count', 'Opp_xG', 'Opp_Count'], inplace=True)

entire_xT, trash = FindingExpectedThreat(entire_actions)
entire_xT = entire_xT.to_frame()
entire_xT.reset_index(inplace=True)
entire_xT['Match Date'] = pd.to_datetime(entire_xT['Match Date']).dt.strftime('%m/%d/%Y')


combined_entire_df = pd.merge(overall_xg, entire_xT, on=['Team', 'Match Date', 'Opposition'], how='outer')
combined_entire_df['Unique Opp and Date'] = combined_entire_df['Opposition'] + ' (' + combined_entire_df['Match Date'] + ')'

possession = pd.read_csv('Veo Data/Veo Analysis - Formatted Games.csv')
possession = possession[['Date', 'Opponent', 'Possession ']]
possession.dropna(inplace=True)
possession['Possession '] = possession['Possession '].str.replace('%', '', regex=False).astype(float)

# Function to determine Team Name based on prefix
def get_team_name(opponent):
    if 'U13' in opponent:
        return 'Boston Bolts U13'
    elif 'U14' in opponent:
        return 'Boston Bolts U14'
    elif 'U15' in opponent:
        return 'Boston Bolts U15'
    elif 'U16' in opponent:
        return 'Boston Bolts U16'
    elif 'U17' in opponent:
        return 'Boston Bolts U17'
    elif 'U19' in opponent:
        return 'Boston Bolts U19'
    return None

# Create 'Team Name' column and clean 'Opponent' column
possession['Team Name'] = possession['Opponent'].apply(get_team_name)
possession['Opponent'] = possession['Opponent'].str.replace(r'^U\d+\s+', '', regex=True)
possession['Date'] = pd.to_datetime(possession['Date']).dt.strftime('%m/%d/%Y')
possession.loc[possession['Opponent'] == 'St Louis', 'Date'] = '12/08/2023'
possession.rename(columns={'Date': 'Match Date', 
                           'Team Name': 'Team', 
                           'Opponent': 'Opposition'}, inplace=True)

combined_entire_df = pd.merge(combined_entire_df, possession, on=['Team', 'Match Date', 'Opposition'], how='inner')
combined_entire_df.rename(columns={'xT': 'xT per 90'}, inplace=True)

opposition = selected_opp
our_team = selected_team
our_date = selected_date
temp_date = selected_date
if temp_date == '12/09/2023':
    temp_date = '12/08/2023'
top3, low3 = PositivesAndNegativesStreamlit(team_select=our_team, opp_select=opposition, date_select=temp_date, comp_opp_select=compare_opp, further_df=combined_entire_df)

change = ['Goal Against', 'Shots on Target Against', 'Loss of Poss', 'Foul Conceded', 'Opp xG per Shot', 'Time Until Regain']

with col3:
    inner_columns = st.columns(2)

    with inner_columns[0]:
        html_string = ( "<span style='font-family: Arial; font-size: 10pt; color: green; "
            "text-decoration: underline; text-decoration-color: green;'><b>Positives</b></span>")
        st.write(html_string, unsafe_allow_html=True)
        for index, cat in top3.items():
            if index in change:
                cat = cat * -1
            player_html = f"<span style='color: green; font-size: 10pt;'>{index}</span> <span style='color: green; font-size: 10pt;'>{round(cat, 2)}</span>"
            st.write(player_html, unsafe_allow_html=True)
    with inner_columns[1]:
        html_string = ( "<span style='font-family: Arial; font-size: 10pt; color: red; "
            "text-decoration: underline; text-decoration-color: red;'><b>Negatives</b></span>")
        st.write(html_string, unsafe_allow_html=True)
        for index, cat in low3.items():
            if index in change:
                cat = cat * -1
            player_html = f"<span style='color: red; font-size: 10pt;'>{index}</span> <span style='color: red; font-size: 10pt'>{round(cat, 2)}</span>"
            st.write(player_html, unsafe_allow_html=True)

player_data_narrow = player_data[['Player Full Name', 'Line Break', 'Pass Completion ', 'Stand. Tackle', 'Tackle']]

player_data_narrow['Total Tackles'] = player_data_narrow['Stand. Tackle'] + player_data_narrow['Tackle']

player_data_narrow.drop(columns={'Stand. Tackle', 'Tackle'}, inplace=True)

full_actions_copy = full_actions.copy()
bolts_xT, player_xT = FindingExpectedThreat(total_events=full_actions_copy)


every_action = actions.copy()
mean_xT, std_xT = MeanAndStdDev(every_action)

if 'U13' in selected_team:
    bolts_xT = (bolts_xT/70) * 90
elif 'U14' in selected_team or 'U15' in selected_team:
    bolts_xT = (bolts_xT/80) * 90


top_xT = player_xT.nlargest(3)
top_xT = top_xT.to_frame()
top_xT.reset_index(inplace=True)
top_tacklers = player_data_narrow.nlargest(3, 'Total Tackles')
top_pass = player_data_narrow.nlargest(3, 'Pass Completion ')

with col3:
    inner_columns = st.columns(3)

    with inner_columns[0]:# Display the HTML string with different styles using unsafe_allow_html=True
        html_string = ( "<span style='font-family: Arial; font-size: 10pt; color: #355870; "
            "text-decoration: underline; text-decoration-color: #355870;'><b>Expected Threat</b></span>")
        st.write(html_string, unsafe_allow_html=True)
        for index, row in top_xT.iterrows():
            player_html = f"<span style='color: #355870; font-size: 10pt;'>{row['Player Full Name']}</span> <span style='color: green; font-size: 10pt;'>{round(row['xT'], 2)}</span>"
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


team_sum = xg_later.groupby('Team')['xG'].sum()

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
    if xg_data['Event'][x] == "Goal" and xg_data['Team'][x] == selected_opp:
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
        <div style='display: flex; justify-content: center;'>
            <span style='font-family: Arial; font-size: 10pt; color: #6bb2e2;'><b>Bolts xG: {bolts_xG}</b></span>
            <span>&nbsp;&nbsp;&nbsp;</span> <!-- Add spaces here -->
            <span style='font-family: Arial; font-size: 10pt; color: black;'><b>{selected_opp} xG: {opp_xG}</b></span>
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

max_goals = game['Goal'].max()
max_assists = game['Assist'].max()
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

# Define a custom sorting function to sort each group by position
def sort_by_position(group):
    return group.sort_values(by='Position')

# Sort starters and substitutes separately by position
starters_sorted = starters.groupby('Position', group_keys=False).apply(sort_by_position)
subs_sorted = subs.groupby('Position', group_keys=False).apply(sort_by_position)

# Concatenate sorted DataFrames
combined_grades = pd.concat([subs_sorted, starters_sorted], ignore_index=True)

# Reset index
combined_grades.reset_index(drop=True, inplace=True)

for index, row in combined_grades.iterrows():
    if row['Player'] == 'Valentin Estevez Rubino':
        combined_grades.at[index, 'Player'] = 'Valentin Estevez-R'
    elif row['Player'] == 'Christian Martinez-Moule':
        combined_grades.at[index, 'Player'] = 'Christian M-M'
    elif row['Player'] == 'Bayron Morales-Vega':
        combined_grades.at[index, 'Player'] = 'Bayron M-V'

fig, ax = plt.subplots(figsize=(8,8), dpi=600)


ncols = 4
nrows = len(combined_grades)

ax.set_xlim(0, 17)
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
            if combined_grades['IsGoalScorer'][i] == 1 and max_goals > 0:
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
            if combined_grades['IsTotalActioner'][i] == 1 and max_totalActions > 0:
                if i in stored:
                    add = 1 + add
                else:
                    add = 0
                img = mpimg.imread('pages/IsTotalActioner.png')
                ax.imshow(img, extent=[positions[j] - 0.5 + add,
                                     positions[j] + 0.5 + add, i-.1, i + 1.1])
                stored.append(i)
            if combined_grades['IsAssister'][i] == 1 and max_assists > 0:
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

image = Image.open('pages/Key3.png')

with col1:
    st.image(image, use_column_width=True)


with col2:
    #inner_columns = st.columns(4)
    inner_columns = st.columns(2)

    #with inner_columns[0]:
    #    fig = plottingBarChart(total_shots, opp_shots, 'Shots')
    #    st.pyplot(fig)
    with inner_columns[0]:
        fig = AttackingPositionOnField(combined_df, full_actions)
        st.pyplot(fig)
    with inner_columns[1]:
        fig = DefendingPositionOnField(combined_df, full_actions)
        st.pyplot(fig)

with col2:
    time_of_poss, time_until_regain = formattingFileForRegain(full_actions)
    time_until_regain = (time_until_regain/total_mins_played) * 990
    fig2 = MiddlePMRStreamlit(team=our_team, opp=opposition, date=our_date, avg_bolts_xg=bolts_mean, avg_opp_xg=opp_mean, our_xT=bolts_xT, avg_xT=mean_xT, 
                              stdev_xT=std_xT, regain_time=time_until_regain)
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot(fig2)


xg_data = xg.copy()

pitch = VerticalPitch(corner_arcs=True, half=True, pitch_type='custom', pitch_length=100, pitch_width=100, line_color='black', line_alpha=0, 
                      pad_bottom=-15, pad_left=-12.5, pad_right=-12.5)  # extend the bottom axis 20 data units)
fig1, axs = pitch.grid(figheight=6, title_height=0.08, endnote_space=0,
                      axis=False, title_space=0, grid_height=0.82)

background_img = plt.imread('C:/Users/Owner/Downloads/SoccermaticsForPython-master/SoccermaticsForPython-master/pages/soccer_field_bw.png')
axs['pitch'].imshow(background_img, extent=[0, 100, 70, 100], aspect='auto', zorder=-1)


custom_order = ['Shot', 'Blocked', 'SOT', 'Goal']
xg_data['Event'] = pd.Categorical(xg_data['Event'], categories=custom_order, ordered=True)
xg_data = xg_data.sort_values('Event')

for index, row in xg_data.iterrows():
    if 'Boston Bolts' in row['Team']:
        hteam = row['Team']
        if row['Event'] == 'Goal':
            pitch.scatter(row['X'], row['Y'],
                          s=(row['xG'] * 1000) + 150,
                          c='lightblue',
                          edgecolors='black',
                          marker='o',
                          ax=axs['pitch'], linewidth=2)
        elif row['Event'] == 'SOT':
            pitch.scatter(row['X'], row['Y'],
                   s=(row['xG'] * 1000) + 150,
                   facecolor='none',
                   edgecolors='black', 
                   marker='o',
                   ax=axs['pitch'],  hatch='///', linewidth=2)
        else:
            pitch.scatter(row['X'], row['Y'],
                   s=(row['xG'] * 1000) + 150,
                   facecolor='none',
                   edgecolors='black',
                   marker='o',
                   ax=axs['pitch'], linewidth=2)
        
legend_elements = [
    mpatches.Circle((0, 0), facecolor='lightblue', edgecolor='black', label='Goal'),
    mpatches.Circle((0, 0), facecolor='none', edgecolor='black', hatch='///', label='On Target'),
    mpatches.Circle((0, 0), facecolor='none', edgecolor='black', label='Miss')
]


axs['pitch'].legend(handles=legend_elements, loc='upper right', fontsize=15)

pitch = VerticalPitch(corner_arcs=True, half=True, pitch_type='custom', pitch_length=100, pitch_width=100, line_color='black', line_alpha=0, 
                      pad_bottom=-15, pad_left=-12.5, pad_right=-12.5)  # extend the bottom axis 20 data units)
fig2, axs = pitch.grid(figheight=6, title_height=0.08, endnote_space=0,
                      axis=False, title_space=0, grid_height=0.82)
axs['pitch'].imshow(background_img, extent=[0, 100, 70, 100], aspect='auto', zorder=-1)


custom_order = ['Shot', 'Blocked', 'SOT', 'Goal']
xg_data['Event'] = pd.Categorical(xg_data['Event'], categories=custom_order, ordered=True)
xg_data = xg_data.sort_values('Event')

for index, row in xg_data.iterrows():
    if 'Boston Bolts' not in row['Team']:
        ateam = row['Team']
        if row['Event'] == 'Goal':
            pitch.scatter(row['X'], row['Y'],
                          s=(row['xG'] * 1000) + 150,
                          c='red',
                          edgecolors='black',
                          marker='o',
                          ax=axs['pitch'], linewidth=2)
        elif row['Event'] == 'SOT':
            pitch.scatter(row['X'], row['Y'],
                   s=(row['xG'] * 1000) + 150,
                   facecolor='none',
                   edgecolors='black', 
                   marker='o',
                   ax=axs['pitch'],  hatch='///', linewidth=2)
        else:
            pitch.scatter(row['X'], row['Y'],
                   s=(row['xG'] * 1000) + 150,
                   facecolor='none',
                   edgecolors='black',
                   marker='o',
                   ax=axs['pitch'], linewidth=2)
        
legend_elements = [
    mpatches.Circle((0, 0), facecolor='red', edgecolor='black', label='Goal'),
    mpatches.Circle((0, 0), facecolor='none', edgecolor='black', hatch='///', label='On Target'),
    mpatches.Circle((0, 0), facecolor='none', edgecolor='black', label='Miss')
]

axs['pitch'].legend(handles=legend_elements, loc='upper right', fontsize=15)
with col2:
    inner_columns = st.columns(2)
    figures = [fig1, fig2]

    for col, img in zip(inner_columns, figures):
        with col:
            st.pyplot(img)


st.session_state["selected_team"] = selected_team
st.session_state["selected_opp"] = selected_opp
st.session_state['selected_date'] = selected_date
