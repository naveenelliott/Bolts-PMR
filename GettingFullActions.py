import pandas as pd
import glob
import os

def UpdatingActions():
    # Path to the folder containing CSV action files
    folder_path = 'PostMatchReviewApp_v2/Actions PSD'

    # Find all CSV files in the folder
    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

    # List to hold individual DataFrames
    df_list = []

    # Loop through the CSV action files and read them into DataFrames
    for file in csv_files:
        df = pd.read_csv(file)
        # formatting the csv files
        df.columns = df.loc[4]
        df = df.loc[5:].reset_index(drop=True)
        # selecting appropriate columns
        df = df[['Player Full Name', 'Team', 'Match Date', 'Opposition', 'Action', 'Period', 
                 'Time', 'x', 'y', 'ex', 'ey', 'Dir']]
        df_list.append(df)

    # Concatenate all DataFrames into a single DataFrame
    combined_df = pd.concat(df_list, ignore_index=True)
    return combined_df


