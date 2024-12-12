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
    drop_table_query = "DROP TABLE IF EXISTS player_position_season_report;"
    cursor.execute(drop_table_query)

    # Load data into DataFrame (replace with your CSV file path)
    df = pd.read_csv('IDP_Report/WeeklyReport PSD/U17_MLSNEXT_Bayside_11092024WR.csv')
    df.columns = df.iloc[3]
    df = df.iloc[4:].reset_index(drop=True)

    # Filter data between "Running By Player" and "Running By Position Player"
    start_index = df.index[df["Period Name"] == "Running By Position Player"][0]
    end_index = df.index[df["Period Name"] == "Running By Team"][0]
    df = df.iloc[start_index:end_index].reset_index(drop=True)

    # Drop unnecessary columns and clean data
    remove_first = ['Period Name', 'Squad Number', 'Match Name', 'As At Date', 'Round Name']
    df = df.drop(columns=remove_first, errors='ignore').dropna(axis=1, how='all').iloc[1:]
    df = df[['Player Full Name', 'mins played', 'Team Name', 'Position Tag', 'Yellow Card', 
             'Red Card', 'Goal', 'Assist', 'Dribble', 'Goal Against', 'Stand. Tackle', 
             'Unsucc Stand. Tackle', 'Tackle', 'Unsucc Tackle', 
             'Clear', 'Own Box Clear', 'Progr Rec', 'Unprogr Rec', 'Progr Inter', 'Unprogr Inter',
             'Progr Regain ', 'Blocked Shot', 'Blocked Cross',
             'Def Aerial Success ', 'Att 1v1', 'Efforts on Goal', 'Shot on Target',
             'Shot off Target', 'Att Shot Blockd', 'Cross', 'Unsucc Cross', 'Efficiency ', 'Long',
             'Unsucc Long', 'Forward', 'Unsucc Forward', 'Line Break', 'Pass into Oppo Box', 'Loss of Poss',
             'Success', 'Unsuccess', 'Pass Completion ', 'Progr Pass Completion ', 'Foul Won', 'Foul Conceded',
             'Save Held', 'Save Parried', 'Save % ', 'Successful Cross', 'PK Missed', 'PK Scored']]
    number_columns = ['mins played', 'Yellow Card', 'Red Card', 'Goal', 'Assist',
                  'Dribble', 'Goal Against', 'Stand. Tackle', 'Unsucc Stand. Tackle', 'Tackle', 'Unsucc Tackle',
                  'Clear', 'Own Box Clear', 'Progr Rec', 'Unprogr Rec', 'Progr Inter', 'Unprogr Inter', 'Progr Regain ',
                  'Blocked Shot', 'Blocked Cross', 'Def Aerial Success ', 'Att 1v1',
                  'Efforts on Goal', 'Shot on Target', 'Shot off Target', 'Att Shot Blockd', 'Cross', 'Unsucc Cross',
                  'Efficiency ', 'Long', 'Unsucc Long', 'Forward', 'Unsucc Forward', 'Line Break', 'Pass into Oppo Box', 'Loss of Poss',
                  'Success', 'Unsuccess', 'Pass Completion ', 'Progr Pass Completion ', 'Foul Won', 'Foul Conceded',
                  'Save Held', 'Save Parried', 'Save % ', 'Successful Cross', 'PK Missed', 'PK Scored']
    df[number_columns] = df[number_columns].astype(float)
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
    df.drop(columns=['Tackles', 'Tackle', 'Stand. Tackle', 'Unsucc Tackle', 'Unsucc Stand. Tackle', 'Clear', 'Own Box Clear', 
                     'Progr Rec', 'Unprogr Rec', 'Progr Inter', 'Unprogr Inter', 'Cross', 'Unsucc Cross',
                     'Long', 'Unsucc Long', 'Forward', 'Unsucc Forward', 'Success', 'Unsuccess', 
                     'Save Held', 'Save Parried'], inplace=True)
    df.rename(columns={'Player Full Name': 'Name',
                       'mins played': 'Minutes', 
                       'Position Tag': 'Position',
                       'Def Aerial Success ': 'Def Aerial %', 
                       'Efforts on Goal': 'Shots',
                       'Efficiency ': 'SOT %', 
                       'Pass Completion ': 'Pass %',
                       'Progr Pass Completion ': 'Progr Pass %',
                       'Successful Cross': 'Crosses Claimed'}, inplace=True)
    
    
    # All converted to per 90
    df['minutes per 90'] = df['Minutes']/90
    
    
    per90 = ['Yellow Card', 'Red Card', 'Goal', 'Assist',
            'Dribble', 'Goal Against', 'Total Tackles', 'Clearances', 'Recoveries', 'Interceptions',
            'Blocked Shot', 'Blocked Cross', 'Att 1v1', 'Total Long Passes', 'Total Forward Passes',
            'Shots', 'Shot on Target', 'Shot off Target', 'Att Shot Blockd', 'Total Crosses', 'Line Break', 
            'Pass into Oppo Box', 'Loss of Poss', 'Total Passes', 'Foul Won', 'Foul Conceded',
            'Total Saves', 'Crosses Claimed', 'PK Missed', 'PK Scored']

    for column in per90:
        if column not in ['Goal', 'Assist', 'Shot on Target', 'Yellow Card', 
                          'Red Card', 'PK Missed', 'PK Scored']:
            df[column] = df[column] / df['minutes per 90']

    df = df.drop(columns=['minutes per 90'])
    
    # Ensure all column names are SQL-friendly (e.g., no spaces)
    df.columns = df.columns.str.replace(' ', '_').str.strip()
    
    df = df.fillna(0)
    
    # Determine the numeric and non-numeric columns
    numeric_columns = [col.replace(' ', '_') for col in number_columns if col.replace(' ', '_') in df.columns]
    numeric_columns = numeric_columns + ['Total_Tackles', 'Tackle_%', 'Clearances', 'Recoveries',
                                         'Interceptions', 'Total_Crosses', 'Cross_%', 'Total_Long_Passes', 
                                         'Long_Pass_%', 'Total_Forward_Passes', 'Total_Passes', 'Total_Saves', 
                                         'Minutes', 'Def_Aerial_%', 'Shots', 'SOT_%', 'Pass_%', 'Progr_Pass_%', 
                                         'Crosses_Claimed']
    
    non_numeric_columns = [col for col in df.columns if col not in numeric_columns]


    # Define table columns dynamically
    numeric_definitions = ", ".join([f"`{col}` FLOAT" for col in numeric_columns])
    non_numeric_definitions = ", ".join([f"`{col}` VARCHAR(255)" for col in non_numeric_columns])
    create_table_query = f"""
    CREATE TABLE player_position_season_report (
        ID INT AUTO_INCREMENT PRIMARY KEY,
        {non_numeric_definitions},
        {numeric_definitions}
    );
    """
    cursor.execute(create_table_query)
    print("Table created successfully.")
        

    # Fetch and display the table content
    select_query = "SELECT * FROM player_position_season_report;"
    cursor.execute(select_query)
    result = cursor.fetchall()

    # Convert to pandas DataFrame for display
    columns = [desc[0] for desc in cursor.description]
    table_df = pd.DataFrame(result, columns=columns)

finally:
    cursor.close()
    connection.close()
