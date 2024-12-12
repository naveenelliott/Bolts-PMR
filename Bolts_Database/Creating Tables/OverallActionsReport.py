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
    drop_table_query = "DROP TABLE IF EXISTS actions_report;"
    cursor.execute(drop_table_query)

    # Load data into DataFrame (replace with your CSV file path)
    df = pd.read_csv('IDP_Report/Actions PSD/u14_ctunitedA.csv')
    df.columns = df.loc[4]
    df = df.loc[5:].reset_index(drop=True)
    
    df = df[['Player Full Name', 'Team', 'Match Date', 'Opposition', 'Action', 'Period', 'Time', 'Video Link']]
    df['Match Date'] = pd.to_datetime(df['Match Date']).dt.strftime('%m/%d/%Y')
    
    df.rename(columns={'Player Full Name': 'Name'}, inplace=True)
    
    # Ensure all column names are SQL-friendly (e.g., no spaces)
    df.columns = df.columns.str.replace(' ', '_').str.strip()
    
    df = df.fillna(0)
    
    non_numeric_columns = df.columns


    # Define table columns dynamically
    non_numeric_definitions = ", ".join(
        [f"`{col}` VARCHAR(255)" if col == "Video Link" else f"`{col}` VARCHAR(100)" for col in non_numeric_columns]
    )

    create_table_query = f"""
    CREATE TABLE actions_report (
        ID INT AUTO_INCREMENT PRIMARY KEY,
        {non_numeric_definitions}
    );
    """
    cursor.execute(create_table_query)
    print("Table created successfully.")

    # Prepare dynamic insert query
    placeholders = ", ".join(["%s"] * len(df.columns))
    insert_query = f"""
    INSERT INTO actions_report ({", ".join([f"`{col}`" for col in df.columns])})
    VALUES ({placeholders});
    """
    
    # Insert rows into the database
    for _, row in df.iterrows():
        cursor.execute(insert_query, tuple(row))
        
        
    # Commit changes
    connection.commit()
    print("Data inserted successfully.")

    # Fetch and display the table content
    select_query = "SELECT * FROM actions_report;"
    cursor.execute(select_query)
    result = cursor.fetchall()

    # Convert to pandas DataFrame for display
    columns = [desc[0] for desc in cursor.description]
    table_df = pd.DataFrame(result, columns=columns)

finally:
    cursor.close()
    connection.close()
