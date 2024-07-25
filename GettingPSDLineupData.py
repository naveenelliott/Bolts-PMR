import pandas as pd
import os

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
            df.columns = df.iloc[3]
            df = df.iloc[4:]
            df = df.reset_index(drop=True)

            start_index = df.index[df["Period Name"] == "Round By Position Player"][0]

            # Find the index where "period name" is equal to "running by position player"
            end_index = df.index[df["Period Name"] == "Round By Team"][0]

            df = df.iloc[start_index:end_index]

            # Reset the index (optional if you want a clean integer index)
            df = df.reset_index(drop=True)
            remove_first = ['Period Name', 'Squad Number', 'Match Name', 'Match Date', 'Round Name']
            df = df.drop(columns=remove_first, errors='ignore')
            df = df.dropna(axis=1, how='all')
            df = df.iloc[1:]
            if 'Starts' in df.columns:
                details = df.loc[:, ['Player Full Name', 'Position Tag', 'Team Name', 'As At Date', 'Opposition', 'Starts']]
                details.rename(columns={'As At Date': 'Date'}, inplace=True)
                details['Date'] = pd.to_datetime(details['Date'], format="%m/%d/%Y %I:%M:%S %p")
                data_frames.append(details)
        
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
    end = end.sort_values('Starts', ascending=False)

    def drop_duplicates_within_group(group):
        # Keep the first occurrence of each group or the one with 'Starts' == 1
        if any(group['Starts'] == 1):
            return group[group['Starts'] == 1].head(1)
        else:
            return group.head(1)

    # Step 4: Apply the function to each group
    end = end.groupby(['Player Full Name', 'Team Name', 'Date', 'Opposition']).apply(drop_duplicates_within_group).reset_index(drop=True)

    end['Opposition'] = end['Opposition'].replace('Seacoast United', 'Seacoast')
    end['Opposition'] = end['Opposition'].replace('Westchester', 'FC Westchester')
    end['Opposition'] = end['Opposition'].replace('FA EURO', 'FA Euro')

    date_condition = end['Date'] > '2024-02-10 00:00:00'

    # Define the condition for excluding specific Oppositions
    exclude_oppositions = ['Albion', 'Miami', 'St Louis']
    opposition_condition = ~end['Opposition'].isin(exclude_oppositions)

    # Combine conditions to filter the DataFrame
    filtered_end = end[date_condition | opposition_condition]

    return end
