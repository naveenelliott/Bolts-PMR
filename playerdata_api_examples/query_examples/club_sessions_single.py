from gqlpython import GraphQLClient
import pandas as pd 
import re


# TODO: Replace with your own values.
CLIENT_ID = "yGhhyBnkZu_VA0Y5Qj0D-snMUQsHwXuq6NCt5S1TTWA"
CLIENT_SECRET = "LFKNJ3ud-vdlhJbCTv1xnJwng-SacBz_WTicW1AYadc"
SESSION_ID = "d7040341-c71f-4948-a4c5-a221da3af1f0"


def session_metrics():
    """
    Fetches metrics for a session.
    """

    # This is the part not working
    client = GraphQLClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )

    # what does this mean?
    with open("graphql_queries/single_session_metrics_query.graphql", "r") as file_stream:
        query = file_stream.read()

    # what does this mean?
    response = client.query(query, {"sessionId": SESSION_ID})

    club_name = response['data']['session']['club']['name']
    session_type = response['data']['session']['__typename']

    start = response['data']['session']['startTime']
    session_participations = response['data']['session']['sessionParticipations']


    flat_data = []

    for participation in session_participations:

            athlete_name = participation['athlete']['name']
            metrics = participation['athleteMetricSet']

            if metrics is not None:
                flat_data.append({
                'athlete_name': athlete_name,
                'total_distance_m': metrics['totalDistanceM'],
                'metres_per_minute': metrics['metresPerMinute'],
                'total_high_intensity_distance_m': metrics['totalHighIntensityDistanceM'],
                'high_intensity_events': metrics['highIntensityEvents'],
                'total_sprint_distance_m': metrics['totalSprintDistanceM'],
                'sprint_events': metrics['sprintEvents'],
                'acceleration_events': metrics['accelerationEvents'],
                'deceleration_events': metrics['decelerationEvents'],
                'max_speed_kph': metrics['maxSpeedKph'],
                'workload': metrics['workload'],
                'workload_volume': metrics['workloadVolume'],
                'workload_intensity': metrics['workloadIntensity']
            })
                
    df = pd.DataFrame(flat_data)

    filename = "playerData.csv"
    df.to_csv(filename, index=False)

if __name__ == "__main__":
    session_metrics()
