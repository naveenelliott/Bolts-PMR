import pandas as pd
import os

def getting_PSD_team_data():
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
            df.columns = df.iloc[3]
            df = df.iloc[4:]
            df = df.reset_index(drop=True)

            start_index = df.index[df["Period Name"] == "Round By Team"][0]

            # Find the index where "period name" is equal to "running by position player"
            end_index = df.index[df["Period Name"] == "Running By Player"][0]

            df = df.iloc[start_index:end_index]

            # Reset the index (optional if you want a clean integer index)
            selected = df.reset_index(drop=True)
            remove_first = ['Period Name', 'Squad Number', 'Match Name', 'As At Date' 'Round Name']
            selected = selected.drop(columns=remove_first, errors='ignore')
            selected = selected.dropna(axis=1, how='all')
            selected = selected.iloc[1:]
            selected['Match Date'] = pd.to_datetime(selected['Match Date']).dt.strftime('%m/%d/%Y')
            selected['Pass Completion '] = selected['Pass Completion '].astype(float)
            selected['Goal Against'] = selected['Goal Against'].astype(float)
            selected['Efforts on Goal'] = selected['Efforts on Goal'].astype(float)
            first_rows = ['Cross', 'Unsucc Cross',  'Forward', 'Unsucc Forward', 
                        'Success', 'Unsuccess', 'Corner Kick', 'Short Corner', 
                        'Unsucc Corner Kick', 'Save Held', 'Save Parried', 'Goal Against']
            selected[first_rows] = selected[first_rows].astype(float)
            selected['Total Cross'] = selected['Cross'] + selected['Unsucc Cross']
            selected['Total Forward'] = selected['Forward'] + selected['Unsucc Forward']
            selected['Total Passes'] = selected['Success'] + selected['Unsuccess']
            selected['Total Corners'] = selected['Corner Kick'] + selected['Short Corner'] + selected['Unsucc Corner Kick']
            selected['Shots on Target Against'] = selected['Save Held'] + selected['Save Parried'] + selected['Goal Against']
            if 'Opp Effort on Goal' in selected.columns:
                selected['Opp Effort on Goal'] = selected['Opp Effort on Goal'].astype(float)
                total_columns = ['Dribble', 'Goal Against',  'Progr Regain ', 'Total Corners', 
                                'Shots on Target Against', 'Team Name', 'Opposition', 'Match Date',
                                'Total Cross', 'Total Forward', 'Att 1v1', 'Efforts on Goal', 'Shot on Target',
                                'Efficiency ', 'Line Break', 'Pass into Oppo Box', 'Opp Effort on Goal',
                                'Loss of Poss', 'Pass Completion ', 'Total Passes', 'Foul Conceded',
                                'Progr Pass Attempt ', 'Progr Pass Completion ', 'Goal', 'Foul Won']
                number_cols = ['Dribble', 'Goal Against',  'Progr Regain ', 'Total Corners', 
                                'Shots on Target Against', 'Opp Effort on Goal',
                                'Total Cross', 'Total Forward', 'Att 1v1', 'Efforts on Goal', 'Shot on Target',
                                    'Efficiency ', 'Line Break', 'Pass into Oppo Box',
                                    'Loss of Poss', 'Pass Completion ', 'Total Passes', 'Foul Conceded',
                                    'Progr Pass Attempt ', 'Progr Pass Completion ', 'Goal', 'Foul Won']
            else:
                total_columns = ['Dribble', 'Goal Against',  'Progr Regain ', 'Total Corners', 
                                'Shots on Target Against', 'Team Name', 'Opposition', 'Match Date',
                                'Total Cross', 'Total Forward', 'Att 1v1', 'Efforts on Goal', 'Shot on Target',
                                    'Efficiency ', 'Line Break', 'Pass into Oppo Box',
                                    'Loss of Poss', 'Pass Completion ', 'Total Passes', 'Foul Conceded',
                                    'Progr Pass Attempt ', 'Progr Pass Completion ', 'Goal', 'Foul Won']
                number_cols = ['Dribble', 'Goal Against',  'Progr Regain ', 'Total Corners', 
                                'Shots on Target Against',
                                'Total Cross', 'Total Forward', 'Att 1v1', 'Efforts on Goal', 'Shot on Target',
                                    'Efficiency ', 'Line Break', 'Pass into Oppo Box',
                                    'Loss of Poss', 'Pass Completion ', 'Total Passes', 'Foul Conceded',
                                    'Progr Pass Attempt ', 'Progr Pass Completion ', 'Goal', 'Foul Won']
            selected = selected.loc[:, total_columns]
            selected[number_cols] = selected[number_cols].astype(float)
            selected.rename(columns={'Match Date': 'Date'}, inplace=True)
            data_frames.append(selected)
        
        # Optionally, combine all DataFrames into a single DataFrame
        combined_df = pd.concat(data_frames, ignore_index=True)
        
        return combined_df

    # Example usage
    folder_path = 'PostMatchReviewApp_v2/Team_Thresholds/BoltsThirteenGames/'  # Replace with your folder path
    bolts13 = read_all_csvs_from_folder(folder_path)
    folder_path = 'PostMatchReviewApp_v2/Team_Thresholds/BoltsFourteenGames/'
    bolts14 = read_all_csvs_from_folder(folder_path)
    folder_path = 'PostMatchReviewApp_v2/Team_Thresholds/BoltsFifteenGames/'
    bolts15 = read_all_csvs_from_folder(folder_path)
    folder_path = 'PostMatchReviewApp_v2/Team_Thresholds/BoltsSixteenGames/'
    bolts16 = read_all_csvs_from_folder(folder_path)
    folder_path = 'PostMatchReviewApp_v2/Team_Thresholds/BoltsSeventeenGames/'
    bolts17 = read_all_csvs_from_folder(folder_path)
    folder_path = 'PostMatchReviewApp_v2/Team_Thresholds/BoltsNineteenGames/'
    bolts19 = read_all_csvs_from_folder(folder_path)

    end = pd.concat([bolts13, bolts14, bolts15, bolts16, bolts17, bolts19])
    #end = end.loc[end['Starts'] == '1']

    age_groups = ['U13', 'U14', 'U15', 'U16', 'U17', 'U19']
    for age_group in age_groups:
        end['Opposition'] = end['Opposition'].str.replace(age_group, '').str.strip()
        
    end = end.drop_duplicates()

    end['Opposition'] = end['Opposition'].replace('Seacoast United', 'Seacoast')
    end['Opposition'] = end['Opposition'].replace('Westchester', 'FC Westchester')
    end['Opposition'] = end['Opposition'].replace('FA EURO', 'FA Euro')

    end['Date'] = pd.to_datetime(end['Date'], format='%m/%d/%Y')

    date_condition = end['Date'] > '2024-02-10 00:00:00'

    # Define the condition for excluding specific Oppositions
    exclude_oppositions = ['Albion', 'Miami', 'St Louis']
    opposition_condition = end['Opposition'].isin(exclude_oppositions)

    # Combine conditions to filter the DataFrame
    filtered_end = end[date_condition | opposition_condition]
    # Drop rows where 'Team Name' is 'Boston Bolts U15' and 'Opposition' is 'Albion'
    filtered_end = filtered_end[~((filtered_end['Team Name'] == 'Boston Bolts U15') & (filtered_end['Opposition'] == 'Albion'))]


    return filtered_end
