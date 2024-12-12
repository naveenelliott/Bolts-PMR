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
    drop_table_query = "DROP TABLE IF EXISTS players_started;"
    cursor.execute(drop_table_query)

    # Recreate the table with an ID column
    create_table_query = """
    CREATE TABLE players_started (
        ID INT AUTO_INCREMENT PRIMARY KEY,
        Name VARCHAR(100) NOT NULL,
        Team_Name VARCHAR(100) NOT NULL,
        Opponent VARCHAR(100) NOT NULL,
        Match_Date VARCHAR(100) NOT NULL,
        Position VARCHAR(100) NOT NULL,
        Started TINYINT(1) NOT NULL
    );
    """
    cursor.execute(create_table_query)
    print("Table recreated successfully.")

    # Load data into DataFrame (replace with your CSV file path)
    df = pd.read_csv('IDP_Report/WeeklyReport PSD/U17_MLSNEXT_Bayside_11092024WR.csv')
    df.columns = df.iloc[3]
    df = df.iloc[4:].reset_index(drop=True)

    # Filter data between "Running By Player" and "Running By Position Player"
    start_index = df.index[df["Period Name"] == "1st Half"][0]
    end_index = df.index[df["Period Name"] == "2nd Half"][0]
    df = df.iloc[start_index:end_index].reset_index(drop=True)

    # Drop unnecessary columns and clean data
    remove_first = ['Period Name', 'Squad Number', 'Match Name', 'As At Date', 'Round Name']
    df = df.drop(columns=remove_first, errors='ignore').dropna(axis=1, how='all').iloc[1:]
    df = df[['Player Full Name', 'Team Name', 'Opposition', 'Match Date', 'Position Tag', 'Starts']]
    df['Match Date'] = pd.to_datetime(df['Match Date']).dt.strftime('%m/%d/%Y')

    # Insert cleaned data into the table
    insert_query = """
    INSERT INTO players_started (Name, Team_Name, Opponent, Match_Date, Position, Started)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    for _, row in df.iterrows():
        cursor.execute(insert_query, (row['Player Full Name'], row['Team Name'],
                                      row['Opposition'], row['Match Date'],
                                      row['Position Tag'], int(row['Starts'])))

    # Commit changes
    connection.commit()
    print("Data inserted successfully.")

    # Fetch and display the table content
    select_query = "SELECT * FROM players_started;"
    cursor.execute(select_query)
    result = cursor.fetchall()

    # Convert to pandas DataFrame for display
    columns = [desc[0] for desc in cursor.description]
    table_df = pd.DataFrame(result, columns=columns)

finally:
    cursor.close()
    connection.close()
