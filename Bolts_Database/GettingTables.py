import mysql.connector
import pandas as pd


def getxGTable():
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
        df = pd.read_sql(query, connection)  # Fetch data into a DataFrame
        return df  # Return the DataFrame
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        connection.close()  # Ensure the connection is closed

def getActionsTable():
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
        query = "SELECT * FROM actions_report;"
        df = pd.read_sql(query, connection)  # Fetch data into a DataFrame
        return df  # Return the DataFrame
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        connection.close()  # Ensure the connection is closed


def getLineupTable():
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
        query = "SELECT * FROM players_started;"
        df = pd.read_sql(query, connection)  # Fetch data into a DataFrame
        return df  # Return the DataFrame
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        connection.close()  # Ensure the connection is closed
    
def getTeamReportTable():
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
        query = "SELECT * FROM team_game_report;"
        df = pd.read_sql(query, connection)  # Fetch data into a DataFrame
        return df  # Return the DataFrame
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        connection.close()  # Ensure the connection is closed

def getPlayerNoPositionTable():
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
        query = "SELECT * FROM player_non_position_game_report;"
        df = pd.read_sql(query, connection)  # Fetch data into a DataFrame
        return df  # Return the DataFrame
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        connection.close()  # Ensure the connection is closed

def getPlayerPositionTable():
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
        query = "SELECT * FROM player_position_game_report;"
        df = pd.read_sql(query, connection)  # Fetch data into a DataFrame
        return df  # Return the DataFrame
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        connection.close()  # Ensure the connection is closed
