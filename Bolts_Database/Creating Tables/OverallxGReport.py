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

def flip_coordinates(x, y):
    # Flip x and y coordinates horizontally
    flipped_x = field_dim - x
    flipped_y = field_dim - y  # y remains unchanged in this transformation
    
    return flipped_x, flipped_y

if connection.is_connected():
    print("Successfully connected to the database")

try:
    cursor = connection.cursor()

    # Drop the existing table if it exists
    drop_table_query = "DROP TABLE IF EXISTS xg_report;"
    cursor.execute(drop_table_query)

    # Load data into DataFrame (replace with your CSV file path)
    df = pd.read_csv('IDP_Report/xG Input Files/u14_ctunitedxG.csv')
    field_dim = 100
    # Iterating through coordinates and making them on one side
    flipped_points = []
    for index, row in df.iterrows():
        if row['X'] < 50:
            flipped_x, flipped_y = flip_coordinates(row['X'], row['Y'])
            df.at[index, 'X'] = flipped_x
            df.at[index, 'Y'] = flipped_y
    
    df.drop(columns=['Mins', 'Secs', 'X2', 'Y2'], inplace=True)
    
    # Ensure all column names are SQL-friendly (e.g., no spaces)
    df.columns = df.columns.str.replace(' ', '_').str.strip()
    
    df = df.fillna(0)
    
    non_numeric_columns = df.columns


    # Define table columns dynamically
    non_numeric_definitions = ", ".join(
        [f"`{col}` VARCHAR(150)" for col in non_numeric_columns]
    )

    create_table_query = f"""
    CREATE TABLE xg_report (
        ID INT AUTO_INCREMENT PRIMARY KEY,
        {non_numeric_definitions}
    );
    """
    cursor.execute(create_table_query)
    print("Table created successfully.")

    # Prepare dynamic insert query
    placeholders = ", ".join(["%s"] * len(df.columns))
    insert_query = f"""
    INSERT INTO xg_report ({", ".join([f"`{col}`" for col in df.columns])})
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
