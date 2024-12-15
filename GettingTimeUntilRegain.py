import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import os
import glob


def formattingFileForRegain(actions):

    def convert_to_timedelta(time_str):
        minutes, seconds = map(int, time_str.split(':'))
        return timedelta(minutes=minutes, seconds=seconds)
    
    actions.columns = actions.columns.str.replace('_', ' ', regex=False)

    actions = actions[['Name', 'Team', 'Match Date', 'Opposition',
                     'Action', 'Period', 'Time']]
    actions = actions.dropna(subset=['Time'])
    
    start = ['Progr Inter', 'Progr Rec', 'Throw', 'Goal Against', 'Ground GK',
             'Short Corner', 'Corner Kick', 'Foul Won',  'Save Held', 'Successful Cross', 'Throw-in']
    end = ['Loss of Poss', 'Unsucc Forward', 'Unsucc Side Back', 'Unsucc Cross', 'Unsucc Long',
           'Goal', 'Save Parried', 'Att Shot Blockd', 'Offside',
           'Shot on Target', 'Shot off Target', 'Header off Target', 'Header on Target', 'Foul Lost']
    start_opp = ['Loss of Poss', 'Unsucc Forward', 'Unsucc Side Back', 'Unsucc Cross', 'Unsucc Long', 
           'Goal', 'Save Parried', 'Att Shot Blockd', 'Offside',
           'Shot on Target', 'Shot off Target', 'Header on Target', 
           'Header off Target', 'Foul Lost']
    end_opp = ['Progr Inter', 'Progr Rec', 'Throw', 'Goal Against', 'Ground GK', 'Throw-in',
             'Short Corner', 'Corner Kick', 'Foul Won', 'Save Held', 'Successful Cross']
    
    def categorize_action(action, desired_list):
        if action in desired_list:
            return 1
        else:
            return 0
    
    # Apply categorization function to create 'Completed Pass' column
    actions['Bolts Start'] = actions['Action'].apply(categorize_action, desired_list=start)
    actions['Bolts End'] = actions['Action'].apply(categorize_action, desired_list=end)
    actions['Opp Start'] = actions['Action'].apply(categorize_action, desired_list=start_opp)
    actions['Opp End'] = actions['Action'].apply(categorize_action, desired_list=end_opp)
    
    completed_action = ['Forward', 'Side Back', 'Dribble', 'Long', 'Loss of Poss', 
                        'Unsucc Forward', 'Unsucc Cross']
    
    actions['Time'] = actions['Time'].apply(convert_to_timedelta)
    
    poss_action = ['Forward', 'Side Back', 'Dribble', 'Long']
    
    for i in range(len(actions) - 1):
        if actions.loc[i, 'Action'] == 'Kick Off' and actions.loc[i, 'Period'] == '1st Half':
            next_action = actions.loc[i + 1, 'Action']
            if next_action in poss_action:
                actions.loc[i, 'Bolts Start'] = 1.0
                flag = True
            else:
                actions.loc[i, 'Opp Start'] = 1.0
                flag = False
    
    for i in range(len(actions)):
        if actions.loc[i, 'Action'] == 'Kick Off' and actions.loc[i, 'Period'] == '2nd Half' and flag == True:
            actions.loc[i, 'Opp Start'] = 1.0
        elif actions.loc[i, 'Action'] == 'Kick Off' and actions.loc[i, 'Period'] == '2nd Half' and flag == False:
            actions.loc[i, 'Bolts Start'] = 1.0
    
    for idx in range(len(actions) - 1):
        # If the next action after an Own Box Clear is a
        if actions.loc[idx, 'Action'] == 'Own Box Clear' and actions.loc[idx + 1, 'Action'] in completed_action and (actions.loc[idx, 'Time'] != actions.loc[idx+1, 'Time']):
            
            # Modify 'Unprogr Rec' row in actions DataFrame
            actions.loc[idx+1, 'Opp End'] = 1.0
            actions.loc[idx+1, 'Bolts Start'] = 1.0
            
    
    for index, row in actions.iterrows():
        if row['Opp Start'] == 1.0 and pd.notna(row['Opp End']):
            # Find the closest Opp End == 1 below Opp Start == 1
            end_index = actions[(actions.index > index) & (actions['Opp End'] == 1.0)].index.min()
            
            if pd.notna(end_index):
                # Check if there's a relevant action in between
                
                if (actions.loc[index:end_index-1, 'Opp End'].any() == 1):
                    continue
                
                actions_between = actions.loc[index+1:end_index-1, 'Action']
                if actions_between.isin(completed_action).any():
                    # Find the time of the action
                    action_time = actions.loc[end_index, 'Time']
                    # Insert a new row before the action
                    new_row = row.copy()
                    new_row['Name'] = ''
                    new_row['Opp Start'] = 0
                    new_row['Opp End'] = 1.0
                    new_row['Bolts Start'] = 1.0
                    new_row['Bolts End'] = 0.0
                    new_row['Action'] = 'Opp Possession End'
                    new_row['Time'] = action_time  # Example adjustment
                    
                    if new_row['Time'] < actions.at[end_index, 'Time']:
                        new_row['Time'] = action_time - timedelta(seconds=1)
                        # Insert the new row above the end_index
                        actions = pd.concat([actions.iloc[:end_index], pd.DataFrame([new_row]), actions.iloc[end_index:]]).reset_index(drop=True)
    
    
    # Initialize variables to track the indices
    last_opp_start_index = None
    last_opp_end_index = None
    
    # List to store indices of rows to drop
    rows_to_drop = []
    
    # Iterate through the DataFrame rows
    for idx, row in actions.iterrows():
        if row['Opp Start'] == 1:
            last_opp_start_index = idx
        elif (row['Opp End'] == 1) and (row['Action'] != 'Opp Possession End'):
            last_opp_end_index = idx
        if row['Action'] == 'Opp Possession End':
            if last_opp_end_index is not None and (last_opp_start_index is None or abs(idx - last_opp_end_index) < abs(idx - last_opp_start_index)):
                rows_to_drop.append(idx)
    
    # Drop the identified rows
    actions.drop(rows_to_drop, inplace=True)
    actions.reset_index(drop=True, inplace=True)
    
    for idx in range(len(actions) - 1):
        if (actions.loc[idx, 'Action'] == 'Unsucc Forward') and (actions.loc[idx + 1, 'Action'] in poss_action):
            
            # Modify 'Unprogr Rec' row in actions DataFrame
            actions.loc[idx+1, 'Opp End'] = 1.0
            actions.loc[idx+1, 'Bolts Start'] = 1.0
    
    rows_to_swap = []
    for i in range(1, len(actions)):
        if  (actions.loc[i, 'Period'] == actions.loc[i-1, 'Period'] and
             actions.loc[i, 'Time'] == actions.loc[i-1, 'Time'] and
            actions.loc[i, 'Opp End'] == 1 and
            actions.loc[i-1, 'Opp Start'] == 1):
            rows_to_swap.append(i)
    
    # Create a new DataFrame with corrected order
    for idx in rows_to_swap:
        actions.iloc[idx], actions.iloc[idx - 1] = actions.iloc[idx - 1].copy(), actions.iloc[idx].copy()
    
    actions.reset_index(drop=True, inplace=True)
    
    rows_to_swap = []
    for i in range(1, len(actions)):
        if  (actions.loc[i, 'Period'] == actions.loc[i-1, 'Period'] and
             actions.loc[i, 'Time'] == actions.loc[i-1, 'Time'] and
            actions.loc[i, 'Opp End'] == 1 and
            actions.loc[i-1, 'Opp Start'] == 0):
            rows_to_swap.append(i)
    
    # Create a new DataFrame with corrected order
    for idx in rows_to_swap:
        actions.iloc[idx], actions.iloc[idx - 1] = actions.iloc[idx - 1].copy(), actions.iloc[idx].copy()
    
    actions.reset_index(drop=True, inplace=True)
    
    
    markers_of_possession = ['Forward', 'Side Back', 'Dribble', 'Long']
    
    # Iterate through the DataFrame to check conditions
    for i in range(len(actions)):
        if actions.loc[i, 'Action'] == 'Stand Tackle':
            # Convert Time to datetime
            current_time = pd.to_timedelta(actions.loc[i, 'Time'])
            
            # Define time window
            start_time = current_time - pd.to_timedelta('5s')
            end_time = current_time + pd.to_timedelta('5s')
            
            # Filter rows within the time window
            relevant_rows = actions[(pd.to_timedelta(actions['Time']) >= start_time) &
                                    (pd.to_timedelta(actions['Time']) <= end_time)]
            
            # Check for markers of possession in relevant rows
            if any(relevant_rows['Action'].isin(markers_of_possession)):
                actions.loc[i, 'Bolts Start'] = 0  # Change Bolts Start to 0
                actions.loc[i, 'Opp End'] = 0
                
    actions = actions.loc[actions['Action'] != 'Pass into Oppo Box'].reset_index(drop=True)
    actions = actions.loc[actions['Action'] != 'Line Break'].reset_index(drop=True)
    
    
    groups = actions.groupby('Time').filter(lambda x: 
        {'Unprogr Rec', 'Unsucc Side Back'}.issubset(set(x['Action']))).groupby('Time')
    
    # Function to reorder rows
    def reorder_rows(group):
        loss_of_poss = group[group['Action'] == 'Unsucc Side Back']
        others = group[group['Action'] != 'Unsucc Side Back']
        reordered_group = pd.concat([loss_of_poss, others])
        
        # Reorder indices
        reordered_indices = list(group.index[:-1]) + [group.index[-1]]
        reordered_group.index = reordered_indices
        return reordered_group
    
    # Apply reordering to each group
    reordered_groups = [reorder_rows(group) for _, group in groups]
    
    # Concatenate the reordered groups with the rest of the DataFrame
    other_actions = actions[~actions['Time'].isin(groups.groups.keys())]
    actions = pd.concat([other_actions] + reordered_groups).sort_index()
    
    actions = actions.reset_index(drop=True)
    
    groups = actions.groupby('Time').filter(lambda x: 
        {'Att 1v1', 'Unsucc Cross'}.issubset(set(x['Action']))).groupby('Time')
    
    # Function to reorder rows
    def reorder_rows(group):
        loss_of_poss = group[group['Action'] == 'Att 1v1']
        others = group[group['Action'] != 'Att 1v1']
        reordered_group = pd.concat([loss_of_poss, others])
        
        # Reorder indices
        reordered_indices = list(group.index[:-1]) + [group.index[-1]]
        reordered_group.index = reordered_indices
        return reordered_group
    
    # Apply reordering to each group
    reordered_groups = [reorder_rows(group) for _, group in groups]
    
    # Concatenate the reordered groups with the rest of the DataFrame
    other_actions = actions[~actions['Time'].isin(groups.groups.keys())]
    actions = pd.concat([other_actions] + reordered_groups).sort_index()
    
    actions = actions.reset_index(drop=True)
    
    groups = actions.groupby('Time').filter(lambda x: 
        {'Forward', 'Stand Tackle', 'Progr Rec'}.issubset(set(x['Action']))).groupby('Time')
    
    # Function to reorder rows
    def reorder_rows(group):
        loss_of_poss = group[group['Action'] == 'Progr Rec']
        others = group[group['Action'] != 'Progr Rec']
        reordered_group = pd.concat([loss_of_poss, others])
        
        # Reorder indices
        reordered_indices = list(group.index[:-1]) + [group.index[-1]]
        reordered_group.index = reordered_indices
        return reordered_group
    
    # Apply reordering to each group
    reordered_groups = [reorder_rows(group) for _, group in groups]
    
    # Concatenate the reordered groups with the rest of the DataFrame
    other_actions = actions[~actions['Time'].isin(groups.groups.keys())]
    actions = pd.concat([other_actions] + reordered_groups).sort_index()
    
    actions = actions.reset_index(drop=True)
    
    groups = actions.groupby('Time').filter(lambda x: 
        {'Dribble', 'Unsucc Forward', 'Progr Rec'}.issubset(set(x['Action']))).groupby('Time')
    
    # Function to reorder rows
    def reorder_rows(group):
        loss_of_poss = group[group['Action'] == 'Progr Rec']
        others = group[group['Action'] != 'Progr Rec']
        reordered_group = pd.concat([loss_of_poss, others])
        
        # Reorder indices
        reordered_indices = list(group.index[:-1]) + [group.index[-1]]
        reordered_group.index = reordered_indices
        return reordered_group
    
    # Apply reordering to each group
    reordered_groups = [reorder_rows(group) for _, group in groups]
    
    # Concatenate the reordered groups with the rest of the DataFrame
    other_actions = actions[~actions['Time'].isin(groups.groups.keys())]
    actions = pd.concat([other_actions] + reordered_groups).sort_index()
    
    actions = actions.reset_index(drop=True)
    
    groups = actions.groupby('Time').filter(lambda x: 
        {'Progr Rec', 'Forward', 'Dribble'}.issubset(set(x['Action']))).groupby('Time')
    
    # Function to reorder rows
    def reorder_rows(group):
        loss_of_poss = group[group['Action'] == 'Progr Rec']
        others = group[group['Action'] != 'Progr Rec']
        reordered_group = pd.concat([loss_of_poss, others])
        
        # Reorder indices
        reordered_indices = list(group.index[:-1]) + [group.index[-1]]
        reordered_group.index = reordered_indices
        return reordered_group
    
    # Apply reordering to each group
    reordered_groups = [reorder_rows(group) for _, group in groups]
    
    # Concatenate the reordered groups with the rest of the DataFrame
    other_actions = actions[~actions['Time'].isin(groups.groups.keys())]
    actions = pd.concat([other_actions] + reordered_groups).sort_index()
    
    actions = actions.reset_index(drop=True)
    
    
    groups = actions.groupby('Time').filter(lambda x: 
        {'Progr Rec', 'Own Box Clear'}.issubset(set(x['Action']))).groupby('Time')
    
    # Function to reorder rows
    def reorder_rows(group):
        loss_of_poss = group[group['Action'] == 'Progr Rec']
        others = group[group['Action'] != 'Progr Rec']
        reordered_group = pd.concat([others, loss_of_poss])
        
        # Reorder indices
        reordered_indices = list(group.index[:-1]) + [group.index[-1]]
        reordered_group.index = reordered_indices
        return reordered_group
    
    # Apply reordering to each group
    reordered_groups = [reorder_rows(group) for _, group in groups]
    
    # Concatenate the reordered groups with the rest of the DataFrame
    other_actions = actions[~actions['Time'].isin(groups.groups.keys())]
    actions = pd.concat([other_actions] + reordered_groups).sort_index()
    
    actions = actions.reset_index(drop=True)
    
    groups = actions.groupby('Time').filter(lambda x: 
        {'Progr Inter', 'Clear'}.issubset(set(x['Action']))).groupby('Time')
    
    # Function to reorder rows
    def reorder_rows(group):
        loss_of_poss = group[group['Action'] == 'Progr Inter']
        others = group[group['Action'] != 'Progr Inter']
        reordered_group = pd.concat([others, loss_of_poss])
        
        # Reorder indices
        reordered_indices = list(group.index[:-1]) + [group.index[-1]]
        reordered_group.index = reordered_indices
        return reordered_group
    
    # Apply reordering to each group
    reordered_groups = [reorder_rows(group) for _, group in groups]
    
    # Concatenate the reordered groups with the rest of the DataFrame
    other_actions = actions[~actions['Time'].isin(groups.groups.keys())]
    actions = pd.concat([other_actions] + reordered_groups).sort_index()
    
    actions = actions.reset_index(drop=True)
    
    groups = actions.groupby('Time').filter(lambda x: 
        {'Tackle', 'Clear'}.issubset(set(x['Action']))).groupby('Time')
    
    # Function to reorder rows
    def reorder_rows(group):
        loss_of_poss = group[group['Action'] == 'Tackle']
        others = group[group['Action'] != 'Tackle']
        reordered_group = pd.concat([others, loss_of_poss])
        
        # Reorder indices
        reordered_indices = list(group.index[:-1]) + [group.index[-1]]
        reordered_group.index = reordered_indices
        return reordered_group
    
    # Apply reordering to each group
    reordered_groups = [reorder_rows(group) for _, group in groups]
    
    # Concatenate the reordered groups with the rest of the DataFrame
    other_actions = actions[~actions['Time'].isin(groups.groups.keys())]
    actions = pd.concat([other_actions] + reordered_groups).sort_index()
    
    actions = actions.reset_index(drop=True)
    
    groups = actions.groupby('Time').filter(lambda x: 
        {'Loss of Poss', 'Foul Lost', 'Unprogr Rec'}.issubset(set(x['Action']))).groupby('Time')
    
    # Function to reorder rows
    def reorder_rows(group):
        loss_of_poss = group[group['Action'] == 'Loss of Poss']
        others = group[group['Action'] != 'Loss of Poss']
        reordered_group = pd.concat([others, loss_of_poss])
        
        # Reorder indices
        reordered_indices = list(group.index[:-1]) + [group.index[-1]]
        reordered_group.index = reordered_indices
        return reordered_group
    
    # Apply reordering to each group
    reordered_groups = [reorder_rows(group) for _, group in groups]
    
    # Concatenate the reordered groups with the rest of the DataFrame
    other_actions = actions[~actions['Time'].isin(groups.groups.keys())]
    actions = pd.concat([other_actions] + reordered_groups).sort_index()
    
    actions = actions.reset_index(drop=True)
    
    groups = actions.groupby('Time').filter(lambda x: 
        {'Loss of Poss', 'Foul Lost', 'Unprogr Rec'}.issubset(set(x['Action']))).groupby('Time')
    
    # Function to reorder rows
    def reorder_rows(group):
        loss_of_poss = group[group['Action'] == 'Unprogr Rec']
        others = group[group['Action'] != 'Unprogr Rec']
        reordered_group = pd.concat([loss_of_poss, others])
        
        # Reorder indices
        reordered_indices = list(group.index[:-1]) + [group.index[-1]]
        reordered_group.index = reordered_indices
        return reordered_group
    
    # Apply reordering to each group
    reordered_groups = [reorder_rows(group) for _, group in groups]
    
    # Concatenate the reordered groups with the rest of the DataFrame
    other_actions = actions[~actions['Time'].isin(groups.groups.keys())]
    actions = pd.concat([other_actions] + reordered_groups).sort_index()
    
    actions = actions.reset_index(drop=True)
    
    groups = actions.groupby('Time').filter(lambda x: 
        {'Progr Rec', 'Foul Won', 'Att Shot Blockd'}.issubset(set(x['Action']))).groupby('Time')
    
    # Function to reorder rows
    def reorder_rows(group):
        loss_of_poss = group[group['Action'] == 'Att Shot Blockd']
        others = group[group['Action'] != 'Att Shot Blockd']
        reordered_group = pd.concat([loss_of_poss, others])
        
        # Reorder indices
        reordered_indices = list(group.index[:-1]) + [group.index[-1]]
        reordered_group.index = reordered_indices
        return reordered_group
    
    # Apply reordering to each group
    reordered_groups = [reorder_rows(group) for _, group in groups]
    
    # Concatenate the reordered groups with the rest of the DataFrame
    other_actions = actions[~actions['Time'].isin(groups.groups.keys())]
    actions = pd.concat([other_actions] + reordered_groups).sort_index()
    
    actions = actions.reset_index(drop=True)
    
    groups = actions.groupby('Time').filter(lambda x: 
        {'Dribble', 'Foul Won', 'Unsucc Forward', 'Att 1v1'}.issubset(set(x['Action']))).groupby('Time')
    
    # Function to reorder rows
    def reorder_rows(group):
        loss_of_poss = group[group['Action'] == 'Unsucc Forward']
        others = group[group['Action'] != 'Unsucc Forward']
        reordered_group = pd.concat([loss_of_poss, others])
        
        # Reorder indices
        reordered_indices = list(group.index[:-1]) + [group.index[-1]]
        reordered_group.index = reordered_indices
        return reordered_group
    
    # Apply reordering to each group
    reordered_groups = [reorder_rows(group) for _, group in groups]
    
    # Concatenate the reordered groups with the rest of the DataFrame
    other_actions = actions[~actions['Time'].isin(groups.groups.keys())]
    actions = pd.concat([other_actions] + reordered_groups).sort_index()
    
    actions = actions.reset_index(drop=True)
    
    
    # Identify rows where 'Unprogr Rec' and 'Unsucc Forward' occur at the same time
    same_time_indices = actions[actions.duplicated(subset=['Time'], keep=False)].index
    remove_indices = []
    
    for idx in same_time_indices:
        if actions.loc[idx, 'Action'] == 'Unprogr Rec' and idx + 1 < len(actions) and (actions.loc[idx + 1, 'Action'] == 'Unsucc Forward'):
            # Adjust time for 'Unprogr Rec' row (example adjustment: 1 second before)
            action_time = pd.to_timedelta(actions.loc[idx, 'Time']) - timedelta(seconds=1)
            
            # Modify 'Unprogr Rec' row in actions DataFrame
            actions.loc[idx, 'Opp End'] = 1.0
            actions.loc[idx, 'Bolts Start'] = 1.0
            actions.loc[idx, 'Time'] = action_time
        elif actions.loc[idx, 'Action'] == 'Unprogr Inter':
            if idx + 1 < len(actions) and actions.loc[idx + 1, 'Action'] == 'Unsucc Forward':
                # Adjust time for 'Unprogr Rec' row (example adjustment: 1 second before)
                action_time = pd.to_timedelta(actions.loc[idx, 'Time']) - timedelta(seconds=1)
                
                # Modify 'Unprogr Rec' row in actions DataFrame
                actions.loc[idx, 'Opp End'] = 1.0
                actions.loc[idx, 'Bolts Start'] = 1.0
                actions.loc[idx, 'Time'] = action_time
        elif actions.loc[idx, 'Action'] == 'Unprogr Rec' and idx + 1 < len(actions) and (actions.loc[idx + 1, 'Action'] == 'Loss of Poss'):
            # Adjust time for 'Unprogr Rec' row (example adjustment: 1 second before)
            action_time = pd.to_timedelta(actions.loc[idx, 'Time']) - timedelta(seconds=1)
            
            # Modify 'Unprogr Rec' row in actions DataFrame
            actions.loc[idx, 'Opp End'] = 1.0
            actions.loc[idx, 'Bolts Start'] = 1.0
            actions.loc[idx, 'Time'] = action_time
        elif actions.loc[idx, 'Action'] == 'Progr Rec' and idx + 1 < len(actions) and actions.loc[idx + 1, 'Action'] in poss_action:
            # Adjust time for 'Unprogr Rec' row (example adjustment: 1 second before)
            action_time = pd.to_timedelta(actions.loc[idx, 'Time']) - timedelta(seconds=1)
            
            # Modify 'Unprogr Rec' row in actions DataFrame
            actions.loc[idx+1, 'Opp End'] = 0
            actions.loc[idx+1, 'Bolts Start'] = 0
        elif actions.loc[idx, 'Action'] == 'Progr Inter' and idx + 1 < len(actions) and actions.loc[idx + 1, 'Action'] in poss_action:
            # Adjust time for 'Unprogr Rec' row (example adjustment: 1 second before)
            action_time = pd.to_timedelta(actions.loc[idx, 'Time']) - timedelta(seconds=1)
            
            # Modify 'Unprogr Rec' row in actions DataFrame
            actions.loc[idx+1, 'Opp End'] = 0
            actions.loc[idx+1, 'Bolts Start'] = 0
        elif actions.loc[idx, 'Action'] == 'Foul Lost' and idx + 1 < len(actions) and actions.loc[idx + 1, 'Action'] == 'Loss of Poss':        
            # Modify 'Unprogr Rec' row in actions DataFrame
            actions.loc[idx, 'Bolts End'] = 0
            actions.loc[idx, 'Opp Start'] = 0
        elif actions.loc[idx, 'Action'] == 'Progr Rec' and idx + 1 < len(actions) and actions.loc[idx + 1, 'Action'] == 'Foul Won':        
            # Modify 'Unprogr Rec' row in actions DataFrame
            actions.loc[idx, 'Bolts Start'] = 0
            actions.loc[idx, 'Opp End'] = 0
        elif actions.loc[idx, 'Action'] == 'Shot on Target' and idx + 1 < len(actions) and actions.loc[idx + 1, 'Action'] == 'Goal':
            # Adjust time for 'Unprogr Rec' row (example adjustment: 1 second before)
            action_time = pd.to_timedelta(actions.loc[idx, 'Time']) - timedelta(seconds=1)
            
            # Modify 'Unprogr Rec' row in actions DataFrame
            actions.loc[idx, 'Bolts End'] = 0
            actions.loc[idx, 'Opp Start'] = 0
        elif actions.loc[idx, 'Action'] == 'Att Shot Blockd' and idx + 1 < len(actions) and actions.loc[idx + 1, 'Action'] == 'Foul Lost':
            # Adjust time for 'Unprogr Rec' row (example adjustment: 1 second before)
            action_time = pd.to_timedelta(actions.loc[idx, 'Time']) - timedelta(seconds=1)
            
            # Modify 'Unprogr Rec' row in actions DataFrame
            actions.loc[idx, 'Bolts End'] = 0
            actions.loc[idx, 'Opp Start'] = 0
        elif actions.loc[idx, 'Action'] == 'Foul Won' and idx + 1 < len(actions) and actions.loc[idx + 1, 'Action'] == 'Progr Rec':
            
            # Modify 'Unprogr Rec' row in actions DataFrame
            actions.loc[idx, 'Opp End'] = 0
            actions.loc[idx, 'Bolts Start'] = 0
        elif actions.loc[idx, 'Action'] == 'Def Aerial' and idx + 1 < len(actions) and actions.loc[idx + 1, 'Action'] in markers_of_possession:
        
            # Modify 'Unprogr Rec' row in actions DataFrame
            actions.loc[idx, 'Opp End'] = 1
            actions.loc[idx, 'Bolts Start'] = 1            
            
    groups = actions.groupby('Time').filter(lambda x: 
        {'Side Back', 'Progr Inter', 'Att 1v1'}.issubset(set(x['Action']))).groupby('Time')
    
    # Function to reorder rows
    def reorder_rows(group):
        loss_of_poss = group[group['Action'] == 'Progr Inter']
        others = group[group['Action'] != 'Progr Inter']
        reordered_group = pd.concat([loss_of_poss, others])
        
        # Reorder indices
        reordered_indices = list(group.index[:-1]) + [group.index[-1]]
        reordered_group.index = reordered_indices
        return reordered_group
    
    # Apply reordering to each group
    reordered_groups = [reorder_rows(group) for _, group in groups]
    
    # Concatenate the reordered groups with the rest of the DataFrame
    other_actions = actions[~actions['Time'].isin(groups.groups.keys())]
    actions = pd.concat([other_actions] + reordered_groups).sort_index()
    
    actions = actions.reset_index(drop=True)
    
    groups = actions.groupby('Time').filter(lambda x: 
        {'Loss of Poss', 'Att 1v1', 'Dribble'}.issubset(set(x['Action']))).groupby('Time')
    
    # Function to reorder rows
    def reorder_rows(group):
        loss_of_poss = group[group['Action'] == 'Loss of Poss']
        others = group[group['Action'] != 'Loss of Poss']
        reordered_group = pd.concat([others, loss_of_poss])
        
        # Reorder indices
        reordered_indices = list(group.index[:-1]) + [group.index[-1]]
        reordered_group.index = reordered_indices
        return reordered_group
    
    # Apply reordering to each group
    reordered_groups = [reorder_rows(group) for _, group in groups]
    
    # Concatenate the reordered groups with the rest of the DataFrame
    other_actions = actions[~actions['Time'].isin(groups.groups.keys())]
    actions = pd.concat([other_actions] + reordered_groups).sort_index()
    
    actions = actions.reset_index(drop=True)
    
    
    groups = actions.groupby('Time').filter(lambda x: 
        {'Throw', 'Save Held'}.issubset(set(x['Action']))).groupby('Time')
    
    # Function to reorder rows
    def reorder_rows(group):
        loss_of_poss = group[group['Action'] == 'Throw']
        others = group[group['Action'] != 'Throw']
        reordered_group = pd.concat([others, loss_of_poss])
        
        # Reorder indices
        reordered_indices = list(group.index[:-1]) + [group.index[-1]]
        reordered_group.index = reordered_indices
        return reordered_group
    
    # Apply reordering to each group
    reordered_groups = [reorder_rows(group) for _, group in groups]
    
    # Concatenate the reordered groups with the rest of the DataFrame
    other_actions = actions[~actions['Time'].isin(groups.groups.keys())]
    actions = pd.concat([other_actions] + reordered_groups).sort_index()
    
    actions = actions.reset_index(drop=True)
    
    groups = actions.groupby('Time').filter(lambda x: 
        {'Loss of Poss', 'Unsucc Stand Tackle'}.issubset(set(x['Action']))).groupby('Time')
    
    # Function to reorder rows
    def reorder_rows(group):
        loss_of_poss = group[group['Action'] == 'Loss of Poss']
        others = group[group['Action'] != 'Loss of Poss']
        reordered_group = pd.concat([others, loss_of_poss])
        
        # Reorder indices
        reordered_indices = list(group.index[:-1]) + [group.index[-1]]
        reordered_group.index = reordered_indices
        return reordered_group
    
    # Apply reordering to each group
    reordered_groups = [reorder_rows(group) for _, group in groups]
    
    # Concatenate the reordered groups with the rest of the DataFrame
    other_actions = actions[~actions['Time'].isin(groups.groups.keys())]
    actions = pd.concat([other_actions] + reordered_groups).sort_index()
    
    actions = actions.reset_index(drop=True)
    
    i = 0
    while i < len(actions) - 1:
        if (actions.loc[i, 'Action'] == 'Unsucc Forward') and (actions.loc[i + 1, 'Action'] == 'Unsucc Cross'):
            new_row = actions.loc[i + 1].copy()
            new_row['Name'] = ''
            new_row['Opp Start'] = 0
            new_row['Opp End'] = 1.0
            new_row['Bolts Start'] = 1.0
            new_row['Bolts End'] = 0.0
            new_row['Action'] = 'Opp Possession End'
            new_row['Time'] = actions.loc[i + 1, 'Time'] - timedelta(seconds=1)
    
            # Insert the new row above the second index
            actions = pd.concat([actions.iloc[:i + 1], pd.DataFrame([new_row]), actions.iloc[i + 1:]]).reset_index(drop=True)
            
            # Skip the next index since we have already checked it
            i += 1
        elif (actions.loc[i, 'Action'] == 'Unprogr Inter') and (actions.loc[i + 1, 'Action'] == 'Loss of Poss'):
            new_row = actions.loc[i + 1].copy()
            new_row['Name'] = ''
            new_row['Opp Start'] = 0
            new_row['Opp End'] = 1.0
            new_row['Bolts Start'] = 1.0
            new_row['Bolts End'] = 0.0
            new_row['Action'] = 'Opp Possession End'
            new_row['Time'] = actions.loc[i + 1, 'Time'] - timedelta(seconds=1)
    
            # Insert the new row above the second index
            actions = pd.concat([actions.iloc[:i], pd.DataFrame([new_row]), actions.iloc[i:]]).reset_index(drop=True)
            
            # Skip the next index since we have already checked it
            i += 1
        elif (actions.loc[i, 'Action'] == 'Unsucc Cross') and (actions.loc[i + 1, 'Action'] == 'Loss of Poss'):
            new_row = actions.loc[i + 1].copy()
            new_row['Name'] = ''
            new_row['Opp Start'] = 0
            new_row['Opp End'] = 1.0
            new_row['Bolts Start'] = 1.0
            new_row['Bolts End'] = 0.0
            new_row['Action'] = 'Opp Possession End'
            new_row['Time'] = actions.loc[i + 1, 'Time'] - timedelta(seconds=1)
    
            # Insert the new row above the second index
            actions = pd.concat([actions.iloc[:i+1], pd.DataFrame([new_row]), actions.iloc[i+1:]]).reset_index(drop=True)
            
            # Skip the next index since we have already checked it
            i += 1
        elif (actions.loc[i, 'Action'] == 'Unsucc Forward') and (actions.loc[i + 1, 'Action'] == 'Loss of Poss'):
            new_row = actions.loc[i + 1].copy()
            new_row['Name'] = ''

            new_row['Opp Start'] = 0
            new_row['Opp End'] = 1.0
            new_row['Bolts Start'] = 1.0
            new_row['Bolts End'] = 0.0
            new_row['Action'] = 'Opp Possession End'
            new_row['Time'] = actions.loc[i + 1, 'Time'] - timedelta(seconds=1)
    
            # Insert the new row above the second index
            actions = pd.concat([actions.iloc[:i+1], pd.DataFrame([new_row]), actions.iloc[i+1:]]).reset_index(drop=True)
            
            # Skip the next index since we have already checked it
            i += 1
        elif (actions.loc[i, 'Action'] == 'Unsucc Forward') and (actions.loc[i + 1, 'Action'] == 'Foul Lost'):
            new_row = actions.loc[i + 1].copy()
            new_row['Name'] = ''
            new_row['Opp Start'] = 0
            new_row['Opp End'] = 1.0
            new_row['Bolts Start'] = 1.0
            new_row['Bolts End'] = 0.0
            new_row['Action'] = 'Opp Possession End'
            new_row['Time'] = actions.loc[i + 1, 'Time'] - timedelta(seconds=1)
    
            # Insert the new row above the second index
            actions = pd.concat([actions.iloc[:i+1], pd.DataFrame([new_row]), actions.iloc[i+1:]]).reset_index(drop=True)
            
            # Skip the next index since we have already checked it
            i += 1
        elif (actions.loc[i, 'Action'] == 'Foul Lost') and (actions.loc[i + 1, 'Action'] == 'Foul Lost'):
            new_row = actions.loc[i + 1].copy()
            new_row['Name'] = ''
            new_row['Opp Start'] = 0
            new_row['Opp End'] = 1.0
            new_row['Bolts Start'] = 1.0
            new_row['Bolts End'] = 0.0
            new_row['Action'] = 'Opp Possession End'
            new_row['Time'] = actions.loc[i + 1, 'Time'] - timedelta(seconds=1)
    
            # Insert the new row above the second index
            actions = pd.concat([actions.iloc[:i+1], pd.DataFrame([new_row]), actions.iloc[i+1:]]).reset_index(drop=True)
            
            # Skip the next index since we have already checked it
            i += 1
        elif (actions.loc[i, 'Action'] == 'Unsucc Forward') and (actions.loc[i + 1, 'Action'] == 'Unsucc Forward'):
            new_row = actions.loc[i + 1].copy()
            new_row['Name'] = ''
            new_row['Opp Start'] = 0
            new_row['Opp End'] = 1.0
            new_row['Bolts Start'] = 1.0
            new_row['Bolts End'] = 0.0
            new_row['Action'] = 'Opp Possession End'
            new_row['Time'] = actions.loc[i + 1, 'Time'] - timedelta(seconds=1)
    
            # Insert the new row above the second index
            actions = pd.concat([actions.iloc[:i+1], pd.DataFrame([new_row]), actions.iloc[i+1:]]).reset_index(drop=True)
            
            # Skip the next index since we have already checked it
            i += 1
        i += 1
        
    for i in range(len(actions) - 1):
        if (actions.loc[i, 'Action'] == 'Stand Tackle') and (actions.loc[i + 1, 'Action'] == 'Progr Rec') and (actions.loc[i, 'Time'] == actions.loc[i + 1, 'Time']):
            actions.loc[i, 'Bolts Start'] = 0.0
            actions.loc[i, 'Opp End'] = 0.0
        elif (actions.loc[i, 'Action'] == 'Progr Rec') and (actions.loc[i + 1, 'Action'] == 'Stand Tackle') and (actions.loc[i, 'Time'] == actions.loc[i + 1, 'Time']):
            actions.loc[i + 1, 'Bolts Start'] = 0.0
            actions.loc[i + 1, 'Opp End'] = 0.0
    
    markers_of_possession.append('Shot on Target')
    markers_of_possession.append('Save Parried')
    markers_of_possession.append('Unsucc Side Back')
    
    for idx in range(len(actions)-1):
        if actions.loc[idx, 'Action'] == 'Loss of Poss' and (actions.loc[idx+1, 'Time'] != actions.loc[idx, 'Time']) and (actions.loc[idx+1, 'Bolts Start'] != 1) and (actions.loc[idx+1, 'Action'] in markers_of_possession):
            actions.loc[idx+1, 'Bolts Start'] = 1
            actions.loc[idx+1, 'Opp End'] = 1
        elif (actions.loc[idx, 'Action'] == 'Unsucc Forward') and (actions.loc[idx+1, 'Time'] != actions.loc[idx, 'Time']) and (actions.loc[idx+1, 'Bolts Start'] == 0) and (actions.loc[idx+1, 'Action'] in markers_of_possession):
            new_row = actions.loc[idx + 1].copy()
            new_row['Name'] = ''
            new_row['Opp Start'] = 0
            new_row['Opp End'] = 1.0
            new_row['Bolts Start'] = 1.0
            new_row['Bolts End'] = 0.0
            new_row['Action'] = 'Opp Possession End'
            new_row['Time'] = actions.loc[idx + 1, 'Time'] - timedelta(seconds=1)
            # Insert the new row above the end_index
            actions = pd.concat([actions.iloc[:idx+1], pd.DataFrame([new_row]), actions.iloc[idx+1:]]).reset_index(drop=True)
        elif actions.loc[idx, 'Action'] == 'Unsucc Cross' and (actions.loc[idx+1, 'Time'] != actions.loc[idx, 'Time']) and (actions.loc[idx+1, 'Bolts Start'] != 1) and (actions.loc[idx+1, 'Action'] == 'Unsucc Forward'):
            new_row = actions.loc[idx + 1].copy()
            new_row['Name'] = ''

            new_row['Opp Start'] = 0
            new_row['Opp End'] = 1.0
            new_row['Bolts Start'] = 1.0
            new_row['Bolts End'] = 0.0
            new_row['Action'] = 'Opp Possession End'
            new_row['Time'] = actions.loc[idx + 1, 'Time'] - timedelta(seconds=1)
            # Insert the new row above the end_index
            actions = pd.concat([actions.iloc[:idx+1], pd.DataFrame([new_row]), actions.iloc[idx+1:]]).reset_index(drop=True) 
        elif actions.loc[idx, 'Action'] == 'Save Parried' and (actions.loc[idx+1, 'Time'] != actions.loc[idx, 'Time']) and (actions.loc[idx+1, 'Bolts Start'] != 1) and (actions.loc[idx+1, 'Action'] == 'Foul Lost'):
            new_row = actions.loc[idx + 1].copy()
            new_row['Name'] = ''

            new_row['Opp Start'] = 0
            new_row['Opp End'] = 1.0
            new_row['Bolts Start'] = 1.0
            new_row['Bolts End'] = 0.0
            new_row['Action'] = 'Opp Possession End'
            new_row['Time'] = actions.loc[idx + 1, 'Time'] - timedelta(seconds=1)
            # Insert the new row above the end_index
            actions = pd.concat([actions.iloc[:idx+1], pd.DataFrame([new_row]), actions.iloc[idx+1:]]).reset_index(drop=True)
        elif actions.loc[idx, 'Action'] == 'Progr Inter' and (actions.loc[idx+1, 'Time'] != actions.loc[idx, 'Time']) and (actions.loc[idx+1, 'Action'] == 'Progr Rec'):
            new_row = actions.loc[idx + 1].copy()
            new_row['Name'] = ''

            new_row['Opp Start'] = 1
            new_row['Opp End'] = 0
            new_row['Bolts Start'] = 0
            new_row['Bolts End'] = 1
            new_row['Action'] = 'Bolts Possession End'
            new_row['Time'] = actions.loc[idx + 1, 'Time'] - timedelta(seconds=1)
            # Insert the new row above the end_index
            actions = pd.concat([actions.iloc[:idx+1], pd.DataFrame([new_row]), actions.iloc[idx+1:]]).reset_index(drop=True)                    
        elif actions.loc[idx, 'Action'] in poss_action and (actions.loc[idx+1, 'Time'] != actions.loc[idx, 'Time']) and (actions.loc[idx+1, 'Action'] == 'Throw'):
            new_row = actions.loc[idx + 1].copy()
            new_row['Name'] = ''

            new_row['Opp Start'] = 1
            new_row['Opp End'] = 0
            new_row['Bolts Start'] = 0
            new_row['Bolts End'] = 1
            new_row['Action'] = 'Bolts Possession End'
            new_row['Time'] = actions.loc[idx + 1, 'Time'] - timedelta(seconds=1)
            # Insert the new row above the end_index
            actions = pd.concat([actions.iloc[:idx+1], pd.DataFrame([new_row]), actions.iloc[idx+1:]]).reset_index(drop=True) 
        elif actions.loc[idx, 'Action'] == 'Short Corner' and (actions.loc[idx+1, 'Time'] != actions.loc[idx, 'Time']) and (actions.loc[idx+1, 'Action'] == 'Unprogr Rec'):
            new_row = actions.loc[idx + 1].copy()
            new_row['Name'] = ''

            new_row['Opp Start'] = 1
            new_row['Opp End'] = 0
            new_row['Bolts Start'] = 0
            new_row['Bolts End'] = 1
            new_row['Action'] = 'Bolts Possession End'
            new_row['Time'] = actions.loc[idx + 1, 'Time'] - timedelta(seconds=1)
            # Insert the new row above the end_index
            actions = pd.concat([actions.iloc[:idx+1], pd.DataFrame([new_row]), actions.iloc[idx+1:]]).reset_index(drop=True) 
        elif actions.loc[idx, 'Action'] == 'Own Box Clear' and (actions.loc[idx+1, 'Time'] != actions.loc[idx, 'Time']) and (actions.loc[idx+1, 'Action'] == 'Progr Inter'):
            new_row = actions.loc[idx + 1].copy()
            new_row['Name'] = ''

            new_row['Opp Start'] = 1
            new_row['Opp End'] = 0
            new_row['Bolts Start'] = 0
            new_row['Bolts End'] = 1
            new_row['Action'] = 'Bolts Possession End'
            new_row['Time'] = actions.loc[idx + 1, 'Time'] - timedelta(seconds=1)
            # Insert the new row above the end_index
            actions = pd.concat([actions.iloc[:idx+1], pd.DataFrame([new_row]), actions.iloc[idx+1:]]).reset_index(drop=True)
        elif actions.loc[idx, 'Action'] == 'Headed Clear' and (actions.loc[idx+1, 'Time'] != actions.loc[idx, 'Time']) and (actions.loc[idx+1, 'Action'] == 'Progr Inter'):
            new_row = actions.loc[idx + 1].copy()
            new_row['Name'] = ''

            new_row['Opp Start'] = 1
            new_row['Opp End'] = 0
            new_row['Bolts Start'] = 0
            new_row['Bolts End'] = 1
            new_row['Action'] = 'Bolts Possession End'
            new_row['Time'] = actions.loc[idx + 1, 'Time'] - timedelta(seconds=1)
            # Insert the new row above the end_index
            actions = pd.concat([actions.iloc[:idx+1], pd.DataFrame([new_row]), actions.iloc[idx+1:]]).reset_index(drop=True)
        elif actions.loc[idx, 'Action'] == 'Forward' and (actions.loc[idx+1, 'Time'] != actions.loc[idx, 'Time']) and (actions.loc[idx+1, 'Action'] == 'Foul Won') and (actions.loc[idx, 'Bolts Start'] == actions.loc[idx+1, 'Bolts Start'] == 1):
            actions.loc[idx+1, 'Bolts Start'] = 0
            actions.loc[idx+1, 'Opp End'] = 0
        elif actions.loc[idx, 'Action'] == 'Forward' and (actions.loc[idx+1, 'Time'] != actions.loc[idx, 'Time']) and (actions.loc[idx+1, 'Action'] == 'Foul Won') and (actions.loc[idx, 'Bolts Start'] != actions.loc[idx+1, 'Bolts Start']):
            actions.loc[idx+1, 'Bolts Start'] = 0
            actions.loc[idx+1, 'Opp End'] = 0
        elif actions.loc[idx, 'Action'] == 'Forward' and (actions.loc[idx+1, 'Time'] != actions.loc[idx, 'Time']) and (actions.loc[idx+1, 'Action'] == 'Opp Possession End') and (actions.loc[idx, 'Bolts Start'] == actions.loc[idx+1, 'Bolts Start'] == 1):
            remove_indices.append(idx+1)
        elif actions.loc[idx, 'Action'] == 'Opp Possession End' and (actions.loc[idx + 1, 'Action'] == 'Unprogr Rec') and (actions.loc[idx, 'Time'] == actions.loc[idx+1, 'Time']) and (actions.loc[idx, 'Bolts Start'] == actions.loc[idx+1, 'Bolts Start']):
            remove_indices.append(idx)
        elif actions.loc[idx+1, 'Action'] == 'Opp Possession End' and (actions.loc[idx, 'Action'] == 'Foul Won') and (actions.loc[idx, 'Time'] != actions.loc[idx+1, 'Time']) and (actions.loc[idx, 'Bolts Start'] == actions.loc[idx+1, 'Bolts Start'] == 1):
            remove_indices.append(idx+1)
        elif actions.loc[idx, 'Action'] == 'Opp Possession End' and (actions.loc[idx-1, 'Action'] == 'Side Back') and (actions.loc[idx+1, 'Action'] == 'Forward') and (actions.loc[idx, 'Time'] != actions.loc[idx+1, 'Time'] != actions.loc[idx-1, 'Time']) and (actions.loc[idx+1, 'Bolts Start'] == actions.loc[idx-1, 'Bolts Start'] == 0):
            remove_indices.append(idx)
        elif actions.loc[idx, 'Action'] == 'Opp Possession End' and (actions.loc[idx-1, 'Action'] == 'Side Back') and (actions.loc[idx, 'Bolts Start'] == actions.loc[idx-1, 'Bolts Start'] == 1):
            remove_indices.append(idx)
        elif actions.loc[idx, 'Action'] == 'Unsucc Cross' and actions.loc[idx + 1, 'Action'] == 'Foul Lost' and (actions.loc[idx, 'Opp Start'] == actions.loc[idx+1, 'Opp Start'] == 1):
        
            # Modify 'Unprogr Rec' row in actions DataFrame
            actions.loc[idx+1, 'Opp Start'] = 0
            actions.loc[idx+1, 'Bolts End'] = 0    
        elif actions.loc[idx, 'Action'] == 'Def Aerial' and actions.loc[idx + 1, 'Action'] in markers_of_possession and (actions.loc[idx, 'Bolts Start'] == actions.loc[idx+1, 'Bolts Start'] == 0):
        
            # Modify 'Unprogr Rec' row in actions DataFrame
            actions.loc[idx, 'Bolts Start'] = 1
            actions.loc[idx, 'Opp End'] = 1
        elif actions.loc[idx, 'Action'] == 'Unsucc Long' and actions.loc[idx + 1, 'Action'] in markers_of_possession and (actions.loc[idx, 'Bolts Start'] == actions.loc[idx+1, 'Bolts Start'] == 0):
        
            # Modify 'Unprogr Rec' row in actions DataFrame
            actions.loc[idx+1, 'Bolts Start'] = 1
            actions.loc[idx+1, 'Opp End'] = 1
        
        
            
        
    actions.drop(remove_indices, inplace=True)
    actions.reset_index(drop=True, inplace=True)  
            
    # Filter the dataframe for '1st Half' period
    first_half_df = actions[actions['Period'] == '1st Half']
    
    # Get the index of the last row in the filtered dataframe
    last_index = first_half_df.index[-1]
    
    # Find the closest row above with Opp Start == 1
    opp_start_indices = first_half_df[(first_half_df['Opp Start'] == 1) & (first_half_df.index <= last_index)].index
    closest_opp_start_index = opp_start_indices[(last_index - opp_start_indices).argmin()] if not opp_start_indices.empty else None
    
    # Find the closest row above with Bolts Start == 1
    bolts_start_indices = first_half_df[(first_half_df['Bolts Start'] == 1) & (first_half_df.index <= last_index)].index
    closest_bolts_start_index = bolts_start_indices[(last_index - bolts_start_indices).argmin()] if not bolts_start_indices.empty else None
    
    # Determine which is closest
    if abs(closest_opp_start_index - last_index) < abs(closest_bolts_start_index - last_index):
        closest_index = closest_opp_start_index
        new_row = {'Period': '1st Half', 'Opp Start': 0, 'Bolts Start': 0, 'Opp End': 1, 'Bolts End': 0, 'Time': actions.loc[last_index, 'Time'], 'Action': 'End of Half'}
    elif abs(closest_opp_start_index - last_index) > abs(closest_bolts_start_index - last_index):
        closest_index = closest_bolts_start_index
        new_row = {'Period': '1st Half', 'Opp Start': 0, 'Bolts Start': 0, 'Opp End': 0, 'Bolts End': 1, 'Time': actions.loc[last_index, 'Time'], 'Action': 'End of Half'}
    actions = pd.concat([actions.iloc[:last_index + 1], pd.DataFrame([new_row]), actions.iloc[last_index + 1:]]).reset_index(drop=True)
    
    second_half_df = actions[actions['Period'] == '2nd Half']
    
    # Get the index of the last row in the filtered dataframe
    last_index = second_half_df.index[-1]
    
    # Find the closest row above with Opp Start == 1
    opp_start_indices = second_half_df[(second_half_df['Opp Start'] == 1) & (second_half_df.index <= last_index)].index
    closest_opp_start_index = opp_start_indices[(last_index - opp_start_indices).argmin()] if not opp_start_indices.empty else None
    
    # Find the closest row above with Bolts Start == 1
    bolts_start_indices = second_half_df[(second_half_df['Bolts Start'] == 1) & (second_half_df.index <= last_index)].index
    closest_bolts_start_index = bolts_start_indices[(last_index - bolts_start_indices).argmin()] if not bolts_start_indices.empty else None
    
    # Determine which is closest
    if abs(closest_opp_start_index - last_index) < abs(closest_bolts_start_index - last_index):
        closest_index = closest_opp_start_index
        new_row = {'Period': '2nd Half', 'Opp Start': 0, 'Bolts Start': 0, 'Opp End': 1, 'Bolts End': 0, 'Time': actions.loc[last_index, 'Time'], 'Action': 'End of Half'}
    elif abs(closest_opp_start_index - last_index) > abs(closest_bolts_start_index - last_index):
        closest_index = closest_bolts_start_index
        new_row = {'Period': '2nd Half', 'Opp Start': 0, 'Bolts Start': 0, 'Opp End': 0, 'Bolts End': 1, 'Time': actions.loc[last_index, 'Time'], 'Action': 'End of Half'}
    actions = pd.concat([actions.iloc[:last_index + 1], pd.DataFrame([new_row]), actions.iloc[last_index + 1:]]).reset_index(drop=True)
    
    for index, row in actions.iterrows():
        if (row['Bolts Start'] == 1) and (row['Opp Start'] == 1):
            bolts_start = actions[(actions.index < index) & (actions['Bolts Start'] == 1)].index.min()
            bolts_start_dist = index - bolts_start
            
            opp_start = actions[(actions.index < index) & (actions['Opp Start'] == 1)].index.min()
            opp_start_dist = index - opp_start
            if bolts_start_dist < opp_start_dist:
                actions.at[index, 'Opp Start'] = 0
                actions.at[index, 'Bolts End'] = 0
            elif opp_start_dist < bolts_start_dist:
                actions.at[index, 'Bolts Start'] = 0
                actions.at[index, 'Opp End'] = 0
    
    actions['Flag'] = ''
    
    actions_end = actions.copy()
    new_rows = []
    
    def filter_bolts_rows(group):
        bolts_start_indices = group.index[group['Bolts Start'] == 1].tolist()
        
        for i in range(1, len(bolts_start_indices)):
            start_idx = bolts_start_indices[i-1]
            next_start_idx = bolts_start_indices[i]
            intermediate_rows = group.loc[start_idx + 1: next_start_idx - 1]
            
            if not (intermediate_rows['Bolts End'] == 1).any():
                group.at[next_start_idx, 'Bolts Start'] = 0
                group.at[next_start_idx, 'Opp End'] = 0
        
        return group
    
    def filter_opp_rows(group):
        opp_start_indices = group.index[group['Opp Start'] == 1].tolist()
        
        for i in range(1, len(opp_start_indices)):
            start_idx = opp_start_indices[i-1]
            next_start_idx = opp_start_indices[i]
            intermediate_rows = group.loc[start_idx + 1: next_start_idx - 1]
            
            if not (intermediate_rows['Opp End'] == 1).any():
                group.at[next_start_idx, 'Opp Start'] = 0
                group.at[next_start_idx, 'Bolts End'] = 0
        
        return group
    
    # Group by 'Time' and apply the filter function
    actions_end = actions_end.groupby('Time').apply(filter_bolts_rows).reset_index(drop=True)
    actions_end = actions_end.groupby('Time').apply(filter_opp_rows).reset_index(drop=True)
    
    for index, row in actions_end.iterrows():
        if row['Opp Start'] == 1.0:
            # Find the closest Opp End == 1 below Opp Start == 1
            end_index = actions_end[(actions_end.index > index) & (actions_end['Bolts Start'] == 1)].index.min()
            
            other_start_index = actions_end[(actions_end.index > index) & (actions_end['Opp Start'] == 1)].index.min()
    
            if pd.notna(end_index) and pd.notna(other_start_index):
                end_diff = end_index - index
                start_diff = other_start_index - index
                time_diff = actions_end.loc[other_start_index, 'Time'] - actions_end.loc[index, 'Time']
                if (start_diff < end_diff) and (time_diff > timedelta(seconds=1)):
                    # Find the time of the action
                    action_time = actions_end.loc[other_start_index, 'Time']
                    # Insert a new row before the action
                    new_row = row.copy()
                    new_row['Name'] = ''
                    new_row['x'] = np.nan
                    new_row['y'] = np.nan
                    new_row['ex'] = np.nan
                    new_row['ey'] = np.nan
                    new_row['Opp Start'] = 0
                    new_row['Opp End'] = 1.0
                    new_row['Bolts Start'] = 1.0
                    new_row['Bolts End'] = 0.0
                    new_row['Action'] = 'Opp Possession End'
                    new_row['Time'] = action_time - timedelta(seconds=1)  # Example adjustment
                    new_rows.append((other_start_index, new_row))
                
    for insertion_index, new_row in sorted(new_rows, reverse=True):
        actions_end = pd.concat([actions_end.iloc[:insertion_index], pd.DataFrame([new_row]), actions_end.iloc[insertion_index:]]).reset_index(drop=True)
    
    
    new_rows = []
    for index, row in actions_end.iterrows():
        if row['Bolts Start'] == 1.0:
            # Find the closest Opp End == 1 below Opp Start == 1
            end_index = actions_end[(actions_end.index > index) & (actions_end['Opp Start'] == 1)].index.min()
            
            other_start_index = actions_end[(actions_end.index > index) & (actions_end['Bolts Start'] == 1)].index.min()
            subset = actions_end.loc[index:other_start_index, 'Action']
            
            if pd.notna(end_index) and pd.notna(other_start_index) and 'End of Half' not in subset.values:
                end_diff = end_index - index
                start_diff = other_start_index - index
                time_diff = actions_end.loc[other_start_index, 'Time'] - actions_end.loc[index, 'Time']
                if (start_diff < end_diff) and (time_diff > timedelta(seconds=1)):
                    # Find the time of the action
                    action_time = actions_end.loc[other_start_index, 'Time']
                    # Insert a new row before the action
                    new_row = row.copy()
                    new_row['Name'] = ''
                    new_row['x'] = np.nan
                    new_row['y'] = np.nan
                    new_row['ex'] = np.nan
                    new_row['ey'] = np.nan
                    new_row['Opp Start'] = 1
                    new_row['Opp End'] = 0
                    new_row['Bolts Start'] = 0
                    new_row['Bolts End'] = 1
                    new_row['Action'] = 'Bolts Possession End'
                    new_row['Time'] = action_time - timedelta(seconds=1)  # Example adjustment
                    new_rows.append((other_start_index, new_row))
                
    for insertion_index, new_row in sorted(new_rows, reverse=True):
        actions_end = pd.concat([actions_end.iloc[:insertion_index], pd.DataFrame([new_row]), actions_end.iloc[insertion_index:]]).reset_index(drop=True)
    
    def gettingRegainAndPossession(poss):
        poss_time = []
        regain_time = []
        for index, row in poss.iterrows():
            if row['Bolts Start'] == 1:
                end_index = poss[(poss.index > index) & (poss['Bolts End'] == 1)].index.min()
                if not pd.isna(end_index):
                    # Calculate the difference in time between the start and end events
                    time_diff = (poss.loc[end_index, 'Time'] - row['Time']).total_seconds()
                    if (time_diff > 2.0) and (poss.loc[index, 'Action'] != 'Opp Possession End'):
                        poss_time.append(time_diff)
            elif row['Opp Start'] == 1:
                end_index = poss[(poss.index > index) & (poss['Opp End'] == 1)].index.min()
                if not pd.isna(end_index):
                    # Calculate the difference in time between the start and end events
                    time_diff = (poss.loc[end_index, 'Time'] - row['Time']).total_seconds()
                    if (time_diff > 2.0) and (poss.loc[index, 'Action'] != 'Bolts Possession End'):
                        regain_time.append(time_diff)
                    
        poss_time = pd.Series(poss_time)
        regain_time = pd.Series(regain_time)
        mean_time_of_poss = poss_time.mean()
        mean_time_regain = regain_time.mean()

        def time_to_seconds(time_str):
            minutes, seconds = map(int, time_str.split(':'))
            return minutes * 60 + seconds
        
        return mean_time_of_poss, mean_time_regain
    
    team = actions_end.at[0, 'Team']
    opp = actions_end.at[0, 'Opposition']
    date = actions_end.at[0, 'Match Date']
    possession_time, time_until_regain = gettingRegainAndPossession(actions_end)
    return possession_time, time_until_regain
