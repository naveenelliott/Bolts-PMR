from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import pandas as pd
import re
from tqdm import tqdm
import requests
import json

mls_next_u13_code = 'd7040341-c71f-4948-a4c5-a221da3af1f0'
mls_next_u14_code = 'e74ca8dc-27dd-4008-b4d3-0d4106ebecac'
mls_next_u15_code = '266c5157-78d6-4792-8f23-306c9791e98d'
mls_next_u16_code = 'dc7608cf-91fd-4e2e-86de-d4e89b0e3d27'
mls_next_u17_code = '71e0abaa-456e-438b-9e54-d50a9f5e2fce'
mls_next_u19_code = 'eda031cf-9836-4c5e-a1d5-e773bb069143'
nal_u13_code = '4004df8e-0d06-40dd-af5f-ece612ab476a'
nal_u14_code = '9664290b-d13c-48a6-95b5-777d62cc1abe'
nal_u15_code = '9bc93b77-9015-48e8-afb2-8cf5a6fa26ab'
nal_u16_code = '2f3f7575-015e-4421-a164-4a0601f50099'
nal_u17_code = '7596f291-f81d-4302-8ee6-b235a79a8829'
nal_u19_code = 'c3c6c7b5-7339-4c1b-b64a-4d10c24f258b'
nal_ss_u13_code = '16343394-5ebe-4d5b-bb28-3579155f48a8'
nal_ss_u14_code = 'f7f19fda-aa38-4135-bdc6-458782ad4f4b'
nal_ss_u15_code = 'bf9fc5fe-ffc0-49d6-accf-8ce7bdbba9c4'
nal_ss_u16_code = 'c978f638-f9f3-4864-8e92-4ac193af64be'
nal_ss_u17_code = 'b5ded3f1-dd97-4d3d-88be-31e59141d8dd'
nal_ss_u19_code = 'ba1f494f-b70a-4888-874a-809bf4a0b585'
gk_code = '02011b28-68c1-4970-91ef-33ded5c09f64'

# TODO: Replace with your own values.
CLIENT_ID = "yGhhyBnkZu_VA0Y5Qj0D-snMUQsHwXuq6NCt5S1TTWA"
CLIENT_SECRET = "LFKNJ3ud-vdlhJbCTv1xnJwng-SacBz_WTicW1AYadc"
CLUB_ID = mls_next_u16_code
MATCH_ID = '87f3613e-d3da-4dd3-9324-dd63155ce635'


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

def club_sessions():
    """
    Fetches metrics for all sessions within a club.
    """
    # not recognizing the client
    transport = RequestsHTTPTransport(
        url="https://app.playerdata.co.uk/api/graphql",  # Replace with your GraphQL endpoint
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        use_json=True,
    )

    client = Client(transport=transport, fetch_schema_from_transport=False)

    with open("playerdata_api_examples/query_examples/graphql_queries/gettingLatLongQuery.graphql", "r") as file_stream:
        query = gql(file_stream.read())

    pbar = tqdm(desc="Fetching Sessions", unit="batch")


    params = {"matchSessionId": MATCH_ID}
    result = client.execute(query, variable_values=params)
    club_name = result['matchSession']["club"]["name"]

    pbar.close()

    # Convert to data frame
    flat_data = []
    start_time = result['matchSession']["startTime"]
    opp = result['matchSession']['opponent']

    bounds = result['matchSession']['pitchCoordinateSet']


    bottom_left_lat = bounds['bottomLeft']['latitude']
    bottom_left_long = bounds['bottomLeft']['longitude']

    bottom_right_lat = bounds['bottomRight']['latitude']
    bottom_right_long = bounds['bottomRight']['longitude']

    top_right_long = bounds['topRight']['longitude']
    top_right_lat = bounds['topRight']['latitude']

    top_left_lat = bounds['topLeft']['latitude']
    top_left_long = bounds['topLeft']['longitude']


    session_participations = result['matchSession']["sessionParticipations"]

    for participation in session_participations:

        athlete_name = participation["athlete"]["name"]
        datafiles = participation['datafiles']
        

        # Loop through each datafile
        for data in datafiles:
            url = data['url']

            try:
                # Send a GET request to the URL
                response = requests.get(url)
                response.raise_for_status()  # Check if the request was successful
                
                # Parse the JSON content
                json_data = response.json()

                fields = ['time', 'satellites', 'longitude', 'latitude']
                
                json_data = [{field: item.get(field) for field in fields} for item in json_data]

                 # Create DataFrame from JSON data
                df = pd.DataFrame(json_data)

                df = df.loc[df['satellites'] >= 10]
                del df['satellites']

                # Add additional fields to DataFrame
                df['start_time'] = start_time
                df['bolts_team'] = club_name
                df['opp_name'] = opp
                df['athlete_name'] = athlete_name
                df['bound_bottom_right_lat'] = bottom_right_lat
                df['bound_bottom_left_lat'] = bottom_left_lat
                df['bound_bottom_right_long'] = bottom_right_long
                df['bound_bottom_left_long'] = bottom_left_long
                df['bound_top_right_lat'] = top_right_lat
                df['bound_top_right_long'] = top_right_long
                df['bound_top_left_lat'] = top_left_lat
                df['bound_top_left_long'] = top_left_long


                # Save the DataFrame to a CSV file
                df.to_csv(f"PlayerDataLatLong/{athlete_name}_{club_name}_LatLong.csv", index=False)
            
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data from {url}: {e}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from {url}: {e}")

    


if __name__ == "__main__":
    club_sessions()
