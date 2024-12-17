from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import pandas as pd
import re
from tqdm import tqdm
import requests
import schedule
import time

# Dictionary of teams with team name as key and their corresponding code as value
team_codes = {
    'MLS Next U13': 'd7040341-c71f-4948-a4c5-a221da3af1f0',
    'MLS Next U14': 'e74ca8dc-27dd-4008-b4d3-0d4106ebecac',
    'MLS Next U15': '266c5157-78d6-4792-8f23-306c9791e98d',
    'MLS Next U16': 'dc7608cf-91fd-4e2e-86de-d4e89b0e3d27',
    'MLS Next U17': '71e0abaa-456e-438b-9e54-d50a9f5e2fce',
    'MLS Next U19': 'eda031cf-9836-4c5e-a1d5-e773bb069143',
    'NAL U13': '4004df8e-0d06-40dd-af5f-ece612ab476a',
    'NAL U14': '9664290b-d13c-48a6-95b5-777d62cc1abe',
    'NAL U15': '9bc93b77-9015-48e8-afb2-8cf5a6fa26ab',
    'NAL U16': '2f3f7575-015e-4421-a164-4a0601f50099',
    'NAL U17': '7596f291-f81d-4302-8ee6-b235a79a8829',
    'NAL U19': 'c3c6c7b5-7339-4c1b-b64a-4d10c24f258b',
    'NAL SS U13': '16343394-5ebe-4d5b-bb28-3579155f48a8',
    'NAL SS U14': 'f7f19fda-aa38-4135-bdc6-458782ad4f4b',
    'NAL SS U15': 'bf9fc5fe-ffc0-49d6-accf-8ce7bdbba9c4',
    'NAL SS U16': 'c978f638-f9f3-4864-8e92-4ac193af64be',
    'NAL SS U17': 'b5ded3f1-dd97-4d3d-88be-31e59141d8dd',
    'NAL SS U19': 'ba1f494f-b70a-4888-874a-809bf4a0b585',
    'GK': '02011b28-68c1-4970-91ef-33ded5c09f64'
}

# TODO: Replace with your own values.
CLIENT_ID = "yGhhyBnkZu_VA0Y5Qj0D-snMUQsHwXuq6NCt5S1TTWA"
CLIENT_SECRET = "LFKNJ3ud-vdlhJbCTv1xnJwng-SacBz_WTicW1AYadc"

def get_access_token(client_id, client_secret):
    token_url = "https://app.playerdata.co.uk/api/oauth/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }

    response = requests.post(token_url, data=data)
    response.raise_for_status()  # Check if the request was successful

    token_info = response.json()
    return token_info['access_token']

# Obtain the token
access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)

def club_sessions(club_id, club_name):
    """
    Fetches metrics for all sessions within a club.
    """
    transport = RequestsHTTPTransport(
        url="https://app.playerdata.co.uk/api/graphql",  # Replace with your GraphQL endpoint
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        use_json=True,
    )

    client = Client(transport=transport, fetch_schema_from_transport=False)

    with open("playerdata_api_examples/query_examples/graphql_queries/club_sessions_query_all.graphql", "r") as file_stream:
        query = gql(file_stream.read())

    offset = 0
    sessions = []

    pbar = tqdm(desc=f"Fetching Sessions for {club_name}", unit="batch")

    while True:
        params = {"clubId": club_id, "offset": offset}
        result = client.execute(query, variable_values=params)
        club_name_result = result["club"]["name"]
        page_sessions = result["club"]["sessions"]
        sessions.extend(page_sessions)

        pbar.update(1)

        if len(page_sessions) == 0:
            break

        offset += 30

    pbar.close()

    # Convert to data frame
    flat_data = []

    for session in tqdm(sessions, desc=f"Processing Sessions for {club_name}", unit="session"):
        start_time = session["startTime"]
        session_type = session["__typename"]

        if session_type == "MatchSession":
            opponent = session["opponent"]
        else:
            opponent = "NA"

        session_participations = session["sessionParticipations"]

        for participation in session_participations:
            athlete_name = participation["athlete"]["name"]
            metrics = participation["metrics"]

            if metrics is not None:
                flat_data.append(
                    {
                        "session_type": session_type,
                        "start_time": start_time,
                        "opponent": opponent,
                        'bolts team': club_name_result,
                        "athlete_name": athlete_name,
                        "total_distance_m": metrics["totalDistanceM"],
                        "total_high_intensity_distance_m": metrics[
                            "totalHighIntensityDistanceM"
                        ],
                        "max_speed_kph": metrics["maxSpeedKph"],
                    }
                )

    df = pd.DataFrame(flat_data)
    
    # Filter out non-match sessions
    if 'opponent' in df.columns:
        df = df.loc[df['opponent'] != 'NA']

    # Save to CSV
    df.to_csv(f"PlayerData Files/{club_name} Matches.csv", index=False)


def run_club_sessions():
    """ Main function to loop through each team and fetch session data. """
    print("Test worked!")
    for team_name, team_code in team_codes.items():
        club_sessions(club_id=team_code, club_name=team_name)

# Schedule the task every Monday at 10 AM
#schedule.every().monday.at("10:00").do(run_club_sessions)

schedule.every(10).seconds.do(run_club_sessions)

print("Scheduler started. Running tasks every Monday at 10 AM...")

# Keep the scheduler running
while True:
    schedule.run_pending()
    time.sleep(1)