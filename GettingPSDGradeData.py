import pandas as pd
import os

def getting_PSD_grade_data():
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

            # Select the rows between the two indices
            selected_rows = df.iloc[start_index:end_index]

            # Reset the index (optional if you want a clean integer index)
            selected = selected_rows.reset_index(drop=True)

            remove_first = ['Period Name', 'Squad Number', 'Match Name', 'Match Date', 'Round Name']
            selected = selected.drop(columns=remove_first, errors='ignore')
            selected = selected.dropna(axis=1, how='all')
            selected = selected.iloc[1:]
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
    end['Opposition'] = end['Opposition'].replace('Rochester NY', 'Rochester')

    return end
