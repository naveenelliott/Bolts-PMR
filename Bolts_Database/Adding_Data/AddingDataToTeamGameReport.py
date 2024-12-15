import os
import pandas as pd
import mysql.connector
from mysql.connector import Error
import logging
import sys

def addingDataToTeamGameReport():

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Folder path and processed files tracker
    folder_path = 'WeeklyReport PSD/'
    processed_files = set()
    reset_flag = False  # Set this to True to reset processed_files.txt, False to resume normal processing

    # Graceful exit handler
    def signal_handler(sig, frame):
        logging.info("Stopping the script...")
        save_processed_files(processed_files)
        sys.exit(0)


    # Function to load processed files
    def load_processed_files():
        try:
            with open('Bolts_Database/Run/Team_Game_Report.txt', 'r') as f:
                return set(f.read().splitlines())
        except FileNotFoundError:
            return set()

    # Function to save processed files
    def save_processed_files(processed_files):
        with open('Bolts_Database/Run/Team_Game_Report.txt', 'w') as f:
            f.write('\n'.join(processed_files))

    # Function to reset processed files
    def reset_processed_files():
        if os.path.exists('Bolts_Database/Run/Team_Game_Report.txt'):
            os.remove('Bolts_Database/Run/Team_Game_Report.txt')
            logging.info("Reset Team_Game_Report.txt. All files will be reprocessed.")
            

    def process_and_insert(file_path, connection):
        try:
            # Load data into DataFrame (replace with your CSV file path)
            df = pd.read_csv(file_path)
            df.columns = df.iloc[3]
            df = df.iloc[4:].reset_index(drop=True)
            
            # Filter data between "Running By Player" and "Running By Position Player"
            start_index = df.index[df["Period Name"] == "Round By Team"][0]
            end_index = df.index[df["Period Name"] == "Running By Player"][0]
            df = df.iloc[start_index:end_index].reset_index(drop=True)
            
            # Drop unnecessary columns and clean data
            remove_first = ['Period Name', 'Squad Number', 'Match Name', 'As At Date', 'Round Name']
            df = df.drop(columns=remove_first, errors='ignore').dropna(axis=1, how='all').iloc[1:]
            expected_columns = ['Team Name', 'mins played', 'Match Date', 'Yellow Card', 
                    'Red Card', 'Goal', 'Assist', 'Dribble', 'Goal Against', 'Stand. Tackle', 
                    'Unsucc Stand. Tackle', 'Tackle', 'Unsucc Tackle', 
                    'Clear', 'Own Box Clear', 'Progr Rec', 'Unprogr Rec', 'Progr Inter', 'Unprogr Inter',
                    'Progr Regain ', 'Blocked Shot', 'Blocked Cross',
                    'Def Aerial Success ', 'Att 1v1', 'Efforts on Goal', 'Shot on Target',
                    'Shot off Target', 'Att Shot Blockd', 'Cross', 'Unsucc Cross', 'Efficiency ', 'Long',
                    'Unsucc Long', 'Forward', 'Unsucc Forward', 'Line Break', 'Pass into Oppo Box', 'Loss of Poss',
                    'Success', 'Unsuccess', 'Pass Completion ', 'Progr Pass Completion ', 'Foul Won', 'Foul Conceded',
                    'Save Held', 'Save Parried', 'Save % ', 'Successful Cross', 'Opposition', 'Opp Effort on Goal']  
            existing_columns = [col for col in expected_columns if col in df.columns]
            df = df[existing_columns]
            number_columns = ['mins played', 'Yellow Card', 'Red Card', 'Goal', 'Assist',
                        'Dribble', 'Goal Against', 'Stand. Tackle', 'Unsucc Stand. Tackle', 'Tackle', 'Unsucc Tackle',
                        'Clear', 'Own Box Clear', 'Progr Rec', 'Unprogr Rec', 'Progr Inter', 'Unprogr Inter', 'Progr Regain ',
                        'Blocked Shot', 'Blocked Cross', 'Def Aerial Success ', 'Att 1v1',
                        'Efforts on Goal', 'Shot on Target', 'Shot off Target', 'Att Shot Blockd', 'Cross', 'Unsucc Cross',
                        'Efficiency ', 'Long', 'Unsucc Long', 'Forward', 'Unsucc Forward', 'Line Break', 'Pass into Oppo Box', 'Loss of Poss',
                        'Success', 'Unsuccess', 'Pass Completion ', 'Progr Pass Completion ', 'Foul Won', 'Foul Conceded',
                        'Save Held', 'Save Parried', 'Save % ', 'Successful Cross', 'Opp Effort on Goal']
            existing_num_columns = [col for col in number_columns if col in df.columns]
            df[existing_num_columns] = df[existing_num_columns].astype(float)
            df['Match Date'] = pd.to_datetime(df['Match Date']).dt.strftime('%m/%d/%Y')
            df['Tackles'] = df['Tackle'] + df['Stand. Tackle']
            df['Total Tackles'] = df['Tackle'] + df['Stand. Tackle'] + df['Unsucc Tackle'] + df['Unsucc Stand. Tackle']
            df['Tackle %'] = (df['Tackles']/df['Total Tackles']) * 100
            df['Clearances'] = df['Clear'] + df['Own Box Clear']
            df['Recoveries'] = df['Progr Rec'] + df['Unprogr Rec']
            df['Interceptions'] = df['Progr Inter'] + df['Unprogr Inter']
            df['Total Crosses'] = df['Cross'] + df['Unsucc Cross']
            df['Cross %'] = (df['Cross']/df['Total Crosses']) * 100
            df['Total Long Passes'] = df['Long'] + df['Unsucc Long']
            df['Long Pass %'] = (df['Long']/df['Total Long Passes']) * 100
            df['Total Forward Passes'] = df['Forward'] + df['Unsucc Forward']
            df['Total Passes'] = df['Success'] + df['Unsuccess']
            df['Total Saves'] = df['Save Held'] + df['Save Parried']
            df.drop(columns=['Tackle', 'Stand. Tackle', 'Unsucc Tackle', 'Unsucc Stand. Tackle', 'Clear', 'Own Box Clear', 
                            'Progr Rec', 'Unprogr Rec', 'Progr Inter', 'Unprogr Inter', 'Cross', 'Unsucc Cross',
                            'Long', 'Unsucc Long', 'Forward', 'Unsucc Forward', 'Success', 'Unsuccess', 
                            'Save Held', 'Save Parried', 'Tackles'], inplace=True)
            if 'Def Aerial Success ' in df.columns:
                df.rename(columns={
                                'Def Aerial Success ': 'Def Aerial %', 
                                'Efforts on Goal': 'Shots',
                                'Efficiency ': 'SOT %', 
                                'Pass Completion ': 'Pass %',
                                'Progr Pass Completion ': 'Progr Pass %',
                                'Successful Cross': 'Crosses Claimed', 
                                'mins played': 'Minutes'}, inplace=True)
            else:
                df.rename(columns={
                                'Efforts on Goal': 'Shots',
                                'Efficiency ': 'SOT %', 
                                'Pass Completion ': 'Pass %',
                                'Progr Pass Completion ': 'Progr Pass %',
                                'Successful Cross': 'Crosses Claimed', 
                                'mins played': 'Minutes'}, inplace=True)
            
            # All converted to per 90
            df['minutes per 90'] = df['Minutes']/990
            
            
            per90 = ['Yellow Card', 'Red Card', 'Goal', 'Assist',
                    'Dribble', 'Goal Against', 'Total Tackles', 'Clearances', 'Recoveries', 'Interceptions',
                    'Blocked Shot', 'Blocked Cross', 'Att 1v1', 'Total Long Passes', 'Total Forward Passes',
                    'Shots', 'Shot on Target', 'Shot off Target', 'Att Shot Blockd', 'Total Crosses', 'Line Break', 
                    'Pass into Oppo Box', 'Loss of Poss', 'Total Passes', 'Foul Won', 'Foul Conceded',
                    'Total Saves', 'Crosses Claimed', 'PK Missed', 'PK Scored']

            for column in per90:
                if column not in ['Goal', 'Assist', 'Shot on Target', 'Yellow Card', 'Red Card', 'PK Missed', 'PK Scored']:
                    df[column] = df[column] / df['minutes per 90']

            df = df.drop(columns=['minutes per 90'])
            
            # Ensure all column names are SQL-friendly (e.g., no spaces)
            df.columns = df.columns.str.replace(' ', '_').str.strip()
            
            df = df.fillna(0)
            
            cursor = connection.cursor()
            
        
            # Prepare dynamic insert query
            placeholders = ", ".join(["%s"] * len(df.columns))
            insert_query = f"""
            INSERT INTO team_game_report ({", ".join([f"`{col}`" for col in df.columns])})
            VALUES ({placeholders});
            """
            
            
            for _, row in df.iterrows():
                cursor.execute(insert_query, tuple(row))
            connection.commit()
            cursor.close()
        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")

    # Reset processed files if the reset flag is True
    if reset_flag:
        reset_processed_files()

    # Load previously processed files
    processed_files = load_processed_files()

    # Connect to the database
    try:
        connection = mysql.connector.connect(
            host="bostonbolts.cviw8wc8czxn.us-east-2.rds.amazonaws.com",
            user="bostonbolts",
            password="Naveen2!",
            database='bostonbolts_db',
            port=3306
        )

        if connection.is_connected():
            logging.info("Successfully connected to the database")

        # Get a list of all files in the folder
        files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
        
        # Process new files
        for file_name in files:
            if file_name not in processed_files:
                file_path = os.path.join(folder_path, file_name)
                logging.info(f"Processing {file_name}...")
                process_and_insert(file_path, connection)
                processed_files.add(file_name)
                save_processed_files(processed_files)
                logging.info(f"Finished processing {file_name}")
        
        logging.info("All files processed. Exiting...")
    except Error as e:
        logging.error(f"Database connection failed: {e}")
    finally:
        if connection.is_connected():
            connection.close()
            logging.info("Database connection closed.")
