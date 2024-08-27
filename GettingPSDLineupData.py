import pandas as pd
import os
import streamlit as st

def getting_PSD_lineup_data():
    def read_all_csvs_from_folder(folder_path):
        # List all files in the folder
        files = os.listdir(folder_path)
        
        # Filter the list to include only CSV files
        csv_files = [file for file in files if file.endswith('.csv')]
        
        # Read each CSV file and store it in a list of DataFrames
        data_frames = []
        for file in csv_files:
            file_path = os.path.join(folder_path, file)
            df = pd.read_csv(file_path)
            # formatting the files
            df.columns = df.iloc[3]
            df = df.iloc[4:]
            df = df.reset_index(drop=True)
            # this is getting us the player data
            start_index = df.index[df["Period Name"] == "Round By Position Player"][0]

            # Find the index where "period name" is equal to "running by position player"
            end_index = df.index[df["Period Name"] == "Round By Team"][0]

            df = df.iloc[start_index:end_index]

            # Reset the index (optional if you want a clean integer index)
            df = df.reset_index(drop=True)
            remove_first = ['Period Name', 'Squad Number', 'Match Name', 'As At Date', 'Round Name']
            df = df.drop(columns=remove_first, errors='ignore')
            df = df.dropna(axis=1, how='all')
            df = df.iloc[1:]
            # if we have starts included, then we extract starts, otherwise we don't and don't add the dataframe
            if 'Starts' in df.columns:
                # selecting match date information, because that's what actions have
                details = df.loc[:, ['Player Full Name', 'Position Tag', 'Team Name', 'Match Date', 'Opposition', 'Starts']]
                details.rename(columns={'Match Date': 'Date'}, inplace=True)
                details['Date'] = pd.to_datetime(details['Date'], format="%m/%d/%Y %I:%M:%S %p")
                data_frames.append(details)
        
        # Optionally, combine all DataFrames into a single DataFrame
        combined_df = pd.concat(data_frames, ignore_index=True)
        st.write(combined_df)
        return combined_df

    # Example usage
    # THIS COULD NEED CHANGED WITH 18 NEW TEAMS
    folder_path = 'Team_Thresholds/BoltsThirteenGames/'  # Replace with your folder path
    bolts13 = read_all_csvs_from_folder(folder_path)
    folder_path = 'Team_Thresholds/BoltsFourteenGames/'
    bolts14 = read_all_csvs_from_folder(folder_path)
    folder_path = 'Team_Thresholds/BoltsFifteenGames/'
    bolts15 = read_all_csvs_from_folder(folder_path)
    folder_path = 'Team_Thresholds/BoltsSixteenGames/'
    bolts16 = read_all_csvs_from_folder(folder_path)
    folder_path = 'Team_Thresholds/BoltsSeventeenGames/'
    bolts17 = read_all_csvs_from_folder(folder_path)
    folder_path = 'Team_Thresholds/BoltsNineteenGames/'
    bolts19 = read_all_csvs_from_folder(folder_path)

    end = pd.concat([bolts13, bolts14, bolts15, bolts16, bolts17, bolts19])
    #end = end.loc[end['Starts'] == '1']

    # ARE THERE DIFFERENT AGE GROUPS? 
    age_groups = ['U13', 'U14', 'U15', 'U16', 'U17', 'U19']
    for age_group in age_groups:
        end['Opposition'] = end['Opposition'].str.replace(age_group, '').str.strip()
        
    end = end.drop_duplicates()
    end = end.sort_values('Starts', ascending=False)

    def drop_duplicates_within_group(group):
        # Keep the first occurrence of each group or the one with 'Starts' == 1
        if any(group['Starts'] == 1):
            return group[group['Starts'] == 1].head(1)
        else:
            return group.head(1)

    # Step 4: Apply the function to each group, specifically for players who play more than once during the game (think u13/u14)
    end = end.groupby(['Player Full Name', 'Team Name', 'Date', 'Opposition']).apply(drop_duplicates_within_group).reset_index(drop=True)

    end['Opposition'] = end['Opposition'].replace('Seacoast United', 'Seacoast')
    end['Opposition'] = end['Opposition'].replace('Westchester', 'FC Westchester')
    end['Opposition'] = end['Opposition'].replace('FA EURO', 'FA Euro')

    date_condition = end['Date'] > '2024-02-10 00:00:00'

    # Define the condition for excluding specific Oppositions
    exclude_oppositions = ['Albion', 'Miami', 'St Louis']
    opposition_condition = end['Opposition'].isin(exclude_oppositions)

    # Combine conditions to filter the DataFrame
    filtered_end = end[date_condition | opposition_condition]
    filtered_end = filtered_end[~((filtered_end['Team Name'] == 'Boston Bolts U15') & (filtered_end['Opposition'] == 'Albion'))]

    return filtered_end
