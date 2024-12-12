from gqlpython import GraphQLClient
import pandas as pd
import re
from tqdm import tqdm

# TODO: Replace with your own values.
CLIENT_ID = ""
CLIENT_SECRET = ""
CLUB_ID = ""


def club_sessions():
    """
    Fetches metrics for all sessions within a club.
    """
    client = GraphQLClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )

    with open(
        "query_examples/graphql_queries/club_sessions_last_30_days_query.graphql", "r"
    ) as file_stream:
        query = file_stream.read()

    result = client.query(query, {"clubId": CLUB_ID})
    print(result)
    club_name = re.sub(r"[\s]+", "_", result["data"]["club"]["name"])
    sessions = result["data"]["club"]["lastThirtyDaysSessions"]
    print(sessions)

    # Convert to data frame
    flat_data = []

    for session in tqdm(sessions, desc="Processing Sessions", unit="session"):
        session_id = session["id"]
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
                        "session_id": session_id,
                        "session_type": session_type,
                        "start_time": start_time,
                        "opponent": opponent,
                        "athlete_name": athlete_name,
                        "total_distance_m": metrics["totalDistanceM"],
                        "metres_per_minute": metrics["metresPerMinute"],
                        "total_high_intensity_distance_m": metrics[
                            "totalHighIntensityDistanceM"
                        ],
                        "high_intensity_events": metrics["highIntensityEvents"],
                        "total_sprint_distance_m": metrics["totalSprintDistanceM"],
                        "sprint_events": metrics["sprintEvents"],
                        "acceleration_events": metrics["accelerationEvents"],
                        "deceleration_events": metrics["decelerationEvents"],
                        "max_speed_kph": metrics["maxSpeedKph"],
                        "workload": metrics["workload"],
                        "workload_volume": metrics["workloadVolume"],
                        "workload_intensity": metrics["workloadIntensity"],
                    }
                )

    df = pd.DataFrame(flat_data)

    df.to_csv(f"{club_name}_last_thirty_days_sessions", index=False)


if __name__ == "__main__":
    club_sessions()
