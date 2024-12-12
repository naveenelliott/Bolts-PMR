import os
import pandas as pd
import mysql.connector
from mysql.connector import Error
import logging
import signal
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Folder path and processed files tracker
folder_path = 'IDP_Report/WeeklyReport PSD/'
processed_files = set()
reset_flag = True  # Set this to True to reset processed_files.txt, False to resume normal processing

# Graceful exit handler
def signal_handler(sig, frame):
    logging.info("Stopping the script...")
    save_processed_files(processed_files)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Function to load processed files
def load_processed_files():
    try:
        with open('processed_files_1.txt', 'r') as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()

# Function to save processed files
def save_processed_files(processed_files):
    with open('processed_files_1.txt', 'w') as f:
        f.write('\n'.join(processed_files))

# Function to reset processed files
def reset_processed_files():
    if os.path.exists('processed_files_1.txt'):
        os.remove('processed_files_1.txt')
        logging.info("Reset processed_files_1.txt. All files will be reprocessed.")

# Function to process and insert data
def process_and_insert(file_path, connection):
    try:
        # Read the CSV
        df = pd.read_csv(file_path)
        df.columns = df.iloc[3]
        df = df.iloc[4:]
        df = df.reset_index(drop=True)
        
        # Process the data to extract player data
        start_index = df.index[df["Period Name"] == "1st Half"][0]
        end_index = df.index[df["Period Name"] == "2nd Half"][0]
        df = df.iloc[start_index:end_index]
        df = df.reset_index(drop=True)
        remove_first = ['Period Name', 'Squad Number', 'Match Name', 'As At Date', 'Round Name']
        df = df.drop(columns=remove_first, errors='ignore')
        df = df.dropna(axis=1, how='all')
        df = df.iloc[1:]
        df = df[['Player Full Name', 'Team Name', 'Opposition', 'Match Date', 'Position Tag', 'Starts']]
        df['Match Date'] = pd.to_datetime(df['Match Date']).dt.strftime('%m/%d/%Y')
        
        # Insert into the database
        insert_query = """
        INSERT INTO players_started (Name, Team_Name, Opponent, Match_Date, Position, Started)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        cursor = connection.cursor()
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
