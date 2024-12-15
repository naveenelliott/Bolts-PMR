import mysql.connector
import pandas as pd

# Database connection
connection = mysql.connector.connect(
    host="bostonbolts.cviw8wc8czxn.us-east-2.rds.amazonaws.com",
    user="bostonbolts",
    password="Naveen2!",
    database="bostonbolts_db",
    port=3306
)

if connection.is_connected():
    print("Successfully connected to the database")

try:
    cursor = connection.cursor()

    # Drop the existing table if it exists
    drop_table_query = "DROP TABLE IF EXISTS player_position_game_report;"
    cursor.execute(drop_table_query)

    # Load data into DataFrame (replace with your CSV file path)
    df = pd.read_csv('WeeklyReport PSD/U17_MLSNEXT_Bayside_11092024WR.csv')
    df.columns = df.iloc[3]
    df = df.iloc[4:].reset_index(drop=True)

    # Filter data between "Running By Player" and "Running By Position Player"
    start_index = df.index[df["Period Name"] == "Round By Position Player"][0]
    end_index = df.index[df["Period Name"] == "Round By Team"][0]
    df = df.iloc[start_index:end_index].reset_index(drop=True)

    # Drop unnecessary columns and clean data
    remove_first = ['Period Name', 'Squad Number', 'Match Name', 'As At Date', 'Round Name']
    df = df.drop(columns=remove_first, errors='ignore').dropna(axis=1, how='all').iloc[1:]
    df = df[['Player Full Name', 'mins played', 'Team Name', 'Match Date', 'Position Tag', 'Yellow Card', 
             'Red Card', 'Goal', 'Assist', 'Dribble', 'Goal Against', 'Stand. Tackle', 
             'Unsucc Stand. Tackle', 'Tackle', 'Unsucc Tackle', 
             'Clear', 'Own Box Clear', 'Progr Rec', 'Unprogr Rec', 'Progr Inter', 'Unprogr Inter',
             'Progr Regain ', 'Blocked Shot', 'Blocked Cross',
             'Def Aerial Success ', 'Att 1v1', 'Efforts on Goal', 'Shot on Target',
             'Shot off Target', 'Att Shot Blockd', 'Cross', 'Unsucc Cross', 'Efficiency ', 'Long',
             'Unsucc Long', 'Forward', 'Unsucc Forward', 'Line Break', 'Pass into Oppo Box', 'Loss of Poss',
             'Success', 'Unsuccess', 'Pass Completion ', 'Progr Pass Completion ', 'Foul Won', 'Foul Conceded', 'Header on Target', 'Att Aerial',
             'Save Held', 'Save Parried', 'Save % ', 'Successful Cross', 'Opposition', 'Opp Effort on Goal', 'PK Missed', 'PK Scored', 'Starts']]
    number_columns = ['mins played', 'Yellow Card', 'Red Card', 'Goal', 'Assist',
                  'Dribble', 'Goal Against', 'Stand. Tackle', 'Unsucc Stand. Tackle', 'Tackle', 'Unsucc Tackle',
                  'Clear', 'Own Box Clear', 'Progr Rec', 'Unprogr Rec', 'Progr Inter', 'Unprogr Inter', 'Progr Regain ',
                  'Blocked Shot', 'Blocked Cross', 'Def Aerial Success ', 'Att 1v1',
                  'Efforts on Goal', 'Shot on Target', 'Shot off Target', 'Att Shot Blockd', 'Cross', 'Unsucc Cross', 'Header on Target', 'Att Aerial',
                  'Efficiency ', 'Long', 'Unsucc Long', 'Forward', 'Unsucc Forward', 'Line Break', 'Pass into Oppo Box', 'Loss of Poss',
                  'Success', 'Unsuccess', 'Pass Completion ', 'Progr Pass Completion ', 'Foul Won', 'Foul Conceded',
                  'Save Held', 'Save Parried', 'Save % ', 'Successful Cross', 'Opp Effort on Goal', 'PK Missed', 'PK Scored', 'Starts']
    df[number_columns] = df[number_columns].astype(float)
    df['Match Date'] = pd.to_datetime(df['Match Date']).dt.strftime('%m/%d/%Y')
    df.rename(columns={'Player Full Name': 'Name',
                       'mins played': 'Minutes', 
                       'Position Tag': 'Position',
                       'Def Aerial Success ': 'Def Aerial %', 
                       'Efforts on Goal': 'Shots',
                       'Efficiency ': 'SOT %', 
                       'Pass Completion ': 'Pass %',
                       'Progr Pass Completion ': 'Progr Pass %',
                       'Successful Cross': 'Crosses Claimed',
                       'Opp Effort on Goal': 'Opp Shots',
                       'Starts': 'Started'}, inplace=True)
    
    
        
    # All converted to per 90
    df['minutes per 90'] = df['Minutes']/90
    
    # did not do anything for goalkeepers like saves, crosses claimed, opp shots - those are the actual raw numbers
    per90 = ['Yellow Card', 'Red Card', 'Goal', 'Assist',  'Dribble', 'Stand. Tackle', 'Unsucc Stand. Tackle', 'Tackle', 'Unsucc Tackle',
            'Clear', 'Own Box Clear', 'Progr Rec', 'Unprogr Rec', 'Progr Inter', 'Unprogr Inter',
            'Blocked Shot', 'Blocked Cross', 'Att 1v1', 'Shots', 'Shot on Target', 'Shot off Target', 'Att Shot Blockd', 'Cross', 'Unsucc Cross',
            'Long', 'Unsucc Long', 'Forward', 'Unsucc Forward', 'Line Break', 'Pass into Oppo Box', 'Loss of Poss',
            'Success', 'Unsuccess', 'Foul Won', 'Foul Conceded']

    for column in per90:
        if column not in ['Goal', 'Assist', 'Shot on Target', 'Yellow Card', 'Red Card', 'PK Missed', 'PK Scored', 'Starts']:
            df[column] = df[column] / df['minutes per 90']

    df = df.drop(columns=['minutes per 90'])
    
    # Ensure all column names are SQL-friendly (e.g., no spaces)
    df.columns = df.columns.str.replace(' ', '_').str.strip()
    
    df = df.fillna(0)
    
    # Determine the numeric and non-numeric columns
    numeric_columns = [col.replace(' ', '_') for col in number_columns if col.replace(' ', '_') in df.columns]
    numeric_columns = numeric_columns + ['Minutes', 'Def_Aerial_%', 'Shots', 'SOT_%', 'Pass_%', 'Progr_Pass_%', 
                                         'Crosses_Claimed']
    
    non_numeric_columns = [col for col in df.columns if col not in numeric_columns]


    # Define table columns dynamically
    numeric_definitions = ", ".join([f"`{col}` FLOAT" for col in numeric_columns])
    non_numeric_definitions = ", ".join([f"`{col}` VARCHAR(255)" for col in non_numeric_columns])
    create_table_query = f"""
    CREATE TABLE player_position_game_report (
        ID INT AUTO_INCREMENT PRIMARY KEY,
        {non_numeric_definitions},
        {numeric_definitions}
    );
    """
    cursor.execute(create_table_query)
    print("Table created successfully.")

    # Prepare dynamic insert query
    placeholders = ", ".join(["%s"] * len(df.columns))
    insert_query = f"""
    INSERT INTO player_position_game_report ({", ".join([f"`{col}`" for col in df.columns])})
    VALUES ({placeholders});
    """
    
    # Insert rows into the database
    for _, row in df.iterrows():
        cursor.execute(insert_query, tuple(row))
        
        
    # Commit changes
    connection.commit()
    print("Data inserted successfully.")

    # Fetch and display the table content
    select_query = "SELECT * FROM player_position_game_report;"
    cursor.execute(select_query)
    result = cursor.fetchall()

    # Convert to pandas DataFrame for display
    columns = [desc[0] for desc in cursor.description]
    table_df = pd.DataFrame(result, columns=columns)

finally:
    cursor.close()
    connection.close()
