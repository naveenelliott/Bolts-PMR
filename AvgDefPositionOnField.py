import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer.pitch import Pitch
from matplotlib.patches import Circle
import seaborn as sns

def DefendingPositionOnField(details, event_data):
    team_name = details.at[0, 'Team Name']
    details = details.loc[details['Starts'] == 1]
    event_data = event_data[event_data['Action'].isin(['Tackle', 'Def Aerial', 'Progr Rec', 'Own Box Clear',
           'Stand Tackle', 'Unprogr Rec',
           'Headed Clear', 'Save Parried', 'Goal Against', 'Progr Inter',
           'Clear', 'Unsucc Def Aerial', 'Blocked Shot',
           'Unsucc Stand Tackle', 'Foul Lost', 'Unsucc Tackle', 'Unprogr Inter'])]
    
    event_data = event_data.dropna(axis=1, how='all')
    event_data[['x', 'y', 'ex', 'ey']] = event_data[['x', 'y', 'ex', 'ey']].astype(float)
    event_data['Player Full Name'] = event_data['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
    details['Player Full Name'] = details['Player Full Name'].apply(lambda x: x.split(' ', 1)[1])
    for index,row in event_data.iterrows():
    
        if row['Dir'] == 'RL':
            event_data.at[index, 'x'] = 120 - event_data.at[index, 'x']
            event_data.at[index, 'y'] = 80 - event_data.at[index, 'y']
            event_data.at[index, 'ex'] = 120 - event_data.at[index, 'ex']
            event_data.at[index, 'ey'] = 80 - event_data.at[index, 'ey']
            
    def custom_aggregation(x):
        return pd.Series({
            'x_mean': x['x'].mean(),
            'y_mean': x['y'].mean(),
            'count': x['x'].count(),
        })
    
    # Group by 'Player' and apply the custom aggregation function
    player_stats_xy = event_data.groupby(['Player Full Name']).apply(custom_aggregation).reset_index()
    
    # Filter player_stats_xy to include only players who started
    players_started = details.loc[details['Starts'] == 1, 'Player Full Name']
    
    # Filter the DataFrame to include only those players
    player_stats_xy = player_stats_xy[player_stats_xy['Player Full Name'].isin(players_started)]
    
    
    fig, ax = plt.subplots(figsize=(13.5, 8))
    pitch = Pitch(pitch_type="statsbomb", pitch_color="#FFFFFF", line_color="#000000")
    pitch.draw(ax=ax)
    plt.gca().invert_yaxis()       
    
    event_data['is_equal'] = (event_data['x'] == event_data['ex']) & (event_data['y'] == event_data['ey'])
    
    end_data = event_data[['ex', 'ey']]
    end_data.dropna(inplace=True)
    end_data.rename(columns={'ex': 'x', 
                     'ey': 'y'}, inplace=True)
    
    event_data = event_data[['x', 'y', 'is_equal']]
    event_data = event_data.dropna()
    event_data = pd.concat([event_data, end_data], ignore_index=True)
    
    event_data = event_data.loc[(event_data['is_equal'] == False) | (event_data['is_equal'].isna())]
    event_data = event_data[['x', 'y']].reset_index(drop=True)
    
    # Overlay density plot
    sns.kdeplot(data=event_data, x='x', y='y', cmap='Blues', shade=True, ax=ax, bw_adjust=0.225, alpha=0.5)
    
    # Iterate through each row in player_stats_xy
    
    if team_name == 'Boston Bolts U13':
        dist_avg = pd.read_csv('PostMatchReviewApp_v2/ActionsAverages/DefensiveActionsAverageU13.csv')
    elif (team_name == 'Boston Bolts U14') or (team_name == 'Boston Bolts U15'):
        dist_avg = pd.read_csv('PostMatchReviewApp_v2/ActionsAverages/DefensiveActionsAverageU14U15.csv')
    elif (team_name == 'Boston Bolts U16') or (team_name == 'Boston Bolts U17') or (team_name == 'Boston Bolts U19'):
        dist_avg = pd.read_csv('PostMatchReviewApp_v2/ActionsAverages/DefensiveActionsAverageU16U17U19.csv')
    
    player_stats_xy = pd.merge(player_stats_xy, details[['Player Full Name', 'Position Tag']], on='Player Full Name')
    for i, row in player_stats_xy.iterrows():
        if 'RCB' in row['Position Tag'] or 'LCB' in row['Position Tag']:
            player_stats_xy['Position Tag'] = player_stats_xy['Position Tag'].str.replace('RCB', 'CB').str.replace('LCB', 'CB')
        elif 'LB' in row['Position Tag'] or 'RB' in row['Position Tag'] or 'RWB' in row['Position Tag'] or 'LWB' in row['Position Tag'] or 'WingB' in row['Position Tag']:
            player_stats_xy['Position Tag'] = player_stats_xy['Position Tag'].str.replace('LB', 'FB').str.replace('RB', 'FB').str.replace('RWB', 'FB').str.replace('LWB', 'FB').str.replace('WingB', 'FB')
        elif 'RW' in row['Position Tag'] or 'LW' in row['Position Tag']:
            player_stats_xy['Position Tag'] = player_stats_xy['Position Tag'].str.replace('RW', 'Wing').str.replace('LW', 'Wing')
        elif 'ATT' in row['Position Tag']:
            player_stats_xy['Position Tag'] = player_stats_xy['Position Tag'].str.replace('ATT', 'CF')
    
    player_stats_xy = pd.merge(player_stats_xy, dist_avg, on='Position Tag')
    
    
    circles = []
    texts = []
    for index, row in player_stats_xy.iterrows():
        # Create a circle representing the player's position
        circle = Circle((row['x_mean'], row['y_mean']), 0.03*row['Adjusted Rate'], edgecolor='black', facecolor='#6bb2e2', zorder=2)
        circles.append(circle)
        ax.add_patch(circle)
        texts.append(ax.text(row['x_mean'], row['y_mean'], row['Player Full Name'], color='black', size=8, ha='center', 
                             va='center', zorder=3))
    
    return fig
    
