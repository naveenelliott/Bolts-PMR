import pandas as pd
import os

def getting_PSD_grade_data(bolts_team, bolts_opp, bolts_date):
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

            start_index = df.index[df["Period Name"] == "Round By Player"][0]

            # Find the index where "period name" is equal to "running by position player"
            end_index = df.index[df["Period Name"] == "Round By Position Player"][0]

            # Select the rows between the two indices
            selected_rows = df.iloc[start_index:end_index]

            # Reset the index (optional if you want a clean integer index)
            selected = selected_rows.reset_index(drop=True)

            remove_first = ['Period Name', 'Squad Number', 'Match Name', 'As At Date', 'Round Name']
            selected = selected.drop(columns=remove_first, errors='ignore')
            selected = selected.dropna(axis=1, how='all')
            selected = selected.iloc[1:]
            data_frames.append(selected)
        
        # Optionally, combine all DataFrames into a single DataFrame
        combined_df = pd.concat(data_frames, ignore_index=True)
        
        return combined_df

    # Example usage
    folder_path = 'WeeklyReport PSD'  # Replace with your folder path
    end = read_all_csvs_from_folder(folder_path)
    
    end['Match Date'] = end['Match Date'].dt.strftime('%m/%d/%Y')

    #end = end.loc[end['Starts'] == '1']

    end = end.loc[(end['Team Name'] == bolts_team) & (end['Opposition'] == bolts_opp) & (end['Match Date'] == bolts_date)]
    end = end[['Player Full Name', 'Line Break', 'Pass Completion ', 'Stand. Tackle', 'Tackle', 'Dribble']]

    return end
