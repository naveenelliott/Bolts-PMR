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
    # Fetch all rows from the table
    query = "SELECT * FROM xg_report;"
    df = pd.read_sql(query, connection)

    # Identify and remove duplicates
    #deduplicated_df = df.drop_duplicates(subset=['Name', 'Team_Name', 'Match_Date', 'Opposition'], keep='first')

    # Update the database with the deduplicated data
    cursor = connection.cursor()
    
    
    # CAN REMOVE CODE
    # Truncate the table to remove all rows
    #truncate_query = "TRUNCATE TABLE player_position_game_report;"
    #cursor.execute(truncate_query)
    #connection.commit()

    # Insert the deduplicated data back into the table
    #placeholders = ", ".join(["%s"] * len(deduplicated_df.columns))
    #insert_query = f"""
    #INSERT INTO player_position_game_report ({", ".join([f"`{col}`" for col in deduplicated_df.columns])})
    #VALUES ({placeholders});
    #"""
    #cursor.executemany(insert_query, deduplicated_df.values.tolist())
    #connection.commit()
    
    #query = "SELECT * FROM player_position_game_report;"
    #df = pd.read_sql(query, connection)

finally:
    connection.close()
