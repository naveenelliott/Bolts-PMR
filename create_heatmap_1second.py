from pitch_coordinates_gps import PitchCoordinatesGPS
from pitch_coordinates_pitch import PitchCoordinatesPitch
import numpy as np
import pandas as pd
import seaborn as sns
import mplsoccer
import plotly.graph_objects as go
from matplotlib import pyplot as plt
import os
import streamlit as st

def gettingHeatmapGK(pname, opp_name):

    opp_name = pd.to_datetime(opp_name)
    opp_name = opp_name.strftime("%m%d%Y")


    if pname == 'Ben Marro':
        pname = 'Benjamin Marro'
    elif pname == 'Casey Powers':
        pname = 'casey powers'
    
    if opp_name == 'NE Revolution':
        opp_name = 'NE Revs'
    elif opp_name == 'New England Revolution':
        opp_name = 'New England Revs'
    elif opp_name == 'Met Oval':
        opp_name = 'Met oval'   

    folder_path = 'PlayerData LatLong'

    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
        
        # Filter filenames that contain both player_name and opp_name
    matching_file = None
    for f in csv_files:
        if pname in f and opp_name in f:
            matching_file = f
            break  # Stop after finding the first match

    if matching_file:
        file_path = os.path.join(folder_path, matching_file)
        coordinates_df = pd.read_csv(file_path)

        coordinates_df.dropna(subset=['longitude'], inplace=True)
        # Convert time-related columns to datetime for easier comparisons
        coordinates_df['period_1_start_time'] = pd.to_datetime(coordinates_df['period_1_start_time'], utc=True)
        coordinates_df['period_1_end_time'] = pd.to_datetime(coordinates_df['period_1_end_time'], utc=True)
        coordinates_df['period_2_start_time'] = pd.to_datetime(coordinates_df['period_2_start_time'], utc=True)
        coordinates_df['period_2_end_time'] = pd.to_datetime(coordinates_df['period_2_end_time'], utc=True)

        period_1_st = coordinates_df.at[0, 'period_1_start_time']
        period_1_et = coordinates_df.at[0, 'period_1_end_time']
        period_2_st = coordinates_df.at[0, 'period_2_start_time']
        period_2_et = coordinates_df.at[0, 'period_2_end_time']

        coordinates_df['timestamp'] = pd.to_datetime(coordinates_df['timestamp'], utc=True)

        # Extract pitch corner coordinates from DataFrame
        bottom_right_lat = coordinates_df.at[0, 'bound_bottom_right_lat']
        bottom_left_lat = coordinates_df.at[0, 'bound_bottom_left_lat']
        bottom_right_lon = coordinates_df.at[0, 'bound_bottom_right_long'] 
        bottom_left_lon = coordinates_df.at[0, 'bound_bottom_left_long']
        top_right_lat = coordinates_df.at[0, 'bound_top_right_lat']
        top_right_lon = coordinates_df.at[0, 'bound_top_right_long']
        top_left_lat = coordinates_df.at[0, 'bound_top_left_lat']
        top_left_lon = coordinates_df.at[0, 'bound_top_left_long']

        # Define pitch corner coordinates dictionary
        pitch_coordinates = {
            "topLeft": {"latitude": top_left_lat, "longitude": top_left_lon},
            "topRight": {"latitude": top_right_lat, "longitude": top_right_lon}, 
            "bottomRight": {"latitude": bottom_right_lat, "longitude": bottom_right_lon},
            "bottomLeft": {"latitude": bottom_left_lat, "longitude": bottom_left_lon},
        }

        # Initialize GPS coordinates and get pitch dimensions
        pitch_gps = PitchCoordinatesGPS(pitch_coordinates)
        pitch_length_meters = pitch_gps.length
        pitch_width_meters = pitch_gps.width

        # Transform GPS coordinates to pitch coordinates
        location_data = coordinates_df[["latitude", "longitude"]].to_numpy()
        transformed_coordinates = pitch_gps.gps_to_pitch_data(location_data)
        pitch_coordinates_pitch = PitchCoordinatesPitch(pitch_width_meters, pitch_length_meters)

        # Add transformed coordinates to DataFrame
        coordinates_df['x'] = transformed_coordinates[:, 0]
        coordinates_df['y'] = transformed_coordinates[:, 1]

        #Translate coordinates to all above 0
        coordinates_df['x'] = coordinates_df['x'] + pitch_width_meters/2
        coordinates_df['y'] = coordinates_df['y'] + pitch_length_meters/2


        # Determine which period the timestamp falls into
        def determine_period(row):
            if period_1_st <= row['timestamp'] <= period_1_et:
                return 1
            elif period_2_st <= row['timestamp'] <= period_2_et:
                return 2
            return np.nan  # Outside periods

        coordinates_df['period'] = coordinates_df.apply(determine_period, axis=1)

        def adjust_coordinates2(row):
            if row['period'] == 2:
                # Flip coordinates for second half
                return pitch_width_meters - row['x'], pitch_length_meters - row['y']
            return row['x'], row['y']

        coordinates_df[['x', 'y']] = coordinates_df.apply(
            lambda row: pd.Series(adjust_coordinates2(row)), axis=1
        )

        coordinates_df = coordinates_df[
            (coordinates_df['x'] >= 0) & (coordinates_df['x'] <= pitch_width_meters) &
            (coordinates_df['y'] >= 0) & (coordinates_df['y'] <= pitch_length_meters)
        ]



        # Create pitch visualization
        pitch = mplsoccer.pitch.VerticalPitch(
            pitch_type='custom',
            pitch_length=pitch_length_meters,
            pitch_width=pitch_width_meters,
            axis=False,
            label=False
        )

        # Draw pitch
        fig, ax = pitch.draw()
        # Create and save KDE heatmap
        sns_plot = sns.kdeplot(
            data=coordinates_df,
            x='x',
            y='y',
            ax=ax,
            cmap='Blues',
            fill=True,
            levels=5,
            alpha=0.9
        )
    else:
        pitch = mplsoccer.pitch.VerticalPitch(pitch_type='custom',  # example plotting a tracab pitch
                      pitch_length=100, pitch_width=70,
                      axis=False, label=False)  # showing axis labels is optional
        fig, ax = pitch.draw()
        
        ax.text(35, 35, 'No heatmap available',
        va='center', ha='center', fontsize=15, color='lightblue', fontweight='bold')

    return fig