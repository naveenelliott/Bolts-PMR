import pandas as pd
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
import matplotlib.pyplot as plt
from mplsoccer import Pitch, VerticalPitch
import numpy as np
import seaborn as sns
from haversine import haversine
from shapely.geometry import Point, Polygon
import os

def gettingHeatmapGK(pname, opp_name):

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
        lat_long = pd.read_csv(file_path)
    
        float_columns = ['longitude', 'latitude', 'bound_bottom_right_lat', 'bound_bottom_left_lat',
                         'bound_bottom_right_long','bound_bottom_left_long', 'bound_top_right_lat', 'bound_top_right_long',
                         'bound_top_left_lat', 'bound_top_left_long']
        lat_long[float_columns] = lat_long[float_columns].astype(float)
        
        lat_long['timestamp'] = pd.to_datetime(lat_long['timestamp'])
        lat_long['period_1_end_time'] = pd.to_datetime(lat_long['period_1_end_time'])
        lat_long['period_2_start_time'] = pd.to_datetime(lat_long['period_2_start_time'])
        
        lat_long['period_1_end_time'] = lat_long['period_1_end_time'].dt.tz_localize(None)
        lat_long['period_2_start_time'] = lat_long['period_2_start_time'].dt.tz_localize(None)
        
        # Filter rows where timestamp is NOT between period_1_end_time and period_2_start_time
        lat_long = lat_long[~((lat_long['timestamp'] >= lat_long['period_1_end_time']) & 
                              (lat_long['timestamp'] <= lat_long['period_2_start_time']))]
        
        
        
        
        # Extract the corner coordinates
        bottom_left_lat = lat_long['bound_bottom_left_lat'][0]
        bottom_left_long = lat_long['bound_bottom_left_long'][0]
        top_left_lat = lat_long['bound_top_left_lat'][0]
        top_left_long = lat_long['bound_top_left_long'][0]
        bottom_right_lat = lat_long['bound_bottom_right_lat'][0]
        bottom_right_long = lat_long['bound_bottom_right_long'][0]
        top_right_lat = lat_long['bound_top_right_lat'][0]
        top_right_long = lat_long['bound_top_right_long'][0]
            
        pitch_corners = [
            (bottom_left_long, bottom_left_lat),
            (bottom_right_long, bottom_right_lat),
            (top_right_long, top_right_lat),
            (top_left_long, top_left_lat)
        ]
        
        # Create a polygon for the pitch
        pitch_polygon = Polygon(pitch_corners)
        
        # Function to check if a point (longitude, latitude) is within the pitch polygon
        def is_point_in_pitch(row):
            point = Point(row['longitude'], row['latitude'])
            return pitch_polygon.contains(point)
        
        # Apply the function to filter the DataFrame
        lat_long['is_in_pitch'] = lat_long.apply(is_point_in_pitch, axis=1)
        lat_long_filtered = lat_long[lat_long['is_in_pitch']]
        
        # Convert lat/long to x/y relative to the bottom-left corner
        def lat_lon_to_xy(row, bottom_left_lat, bottom_left_long):
            """Convert lat/lon to x/y relative to the bottom-left corner of the pitch."""
            # x is the distance from the bottom left along the latitude (length-wise)
            x = haversine((bottom_left_lat, bottom_left_long), (row['latitude'], bottom_left_long))
            # y is the distance from the bottom left along the longitude (width-wise)
            y = haversine((bottom_left_lat, bottom_left_long), (bottom_left_lat, row['longitude']))
            return pd.Series({'x': x, 'y': y})
        
        lat_long_filtered[['x', 'y']] = lat_long_filtered.apply(
            lat_lon_to_xy, axis=1, bottom_left_lat=bottom_left_lat, bottom_left_long=bottom_left_long
        )
        
        lat_long_filtered[['x', 'y']] = lat_long_filtered[['x', 'y']] * 1000
        
        # Calculate pitch length using the Haversine formula (distance between bottom left and top left)
        pitch_length_meters = haversine((bottom_left_lat, bottom_left_long), (top_left_lat, top_left_long))
        pitch_length_meters = pitch_length_meters * 1000
        
        # Calculate pitch width using the Haversine formula (distance between bottom left and bottom right)
        pitch_width_meters = haversine((bottom_left_lat, bottom_left_long), (bottom_right_lat, bottom_right_long))
        pitch_width_meters = pitch_width_meters * 1000
        
        #pitch_length = pitch_length_meters
        
        
        
        # Remove the 'is_in_pitch' column if it's no longer needed
        lat_long_filtered.drop(columns=['is_in_pitch'], inplace=True)
        
        # Calculate the boundaries for the thirds
        #fourth_boundaries = [0, pitch_length / 4, pitch_length / 2, 3 * pitch_length / 4, pitch_length]
        
        # Assign each point to a third
        #lat_long_filtered['fourths'] = pd.cut(lat_long_filtered['y'], bins=fourth_boundaries, 
         #                                     labels=['Att Quarter', 'Middle Att Quarter', 'Middle Def Quarter', 'Def Quarter'], include_lowest=True)
        
        # Calculate total time spent in each third
        #time_in_fourths = lat_long_filtered.groupby('fourths')['time'].sum()
        
        # Calculate the percentage of time in each third
        #total_time_spent = time_in_fourths.sum()
        #percentage_time_in_fourths = (time_in_fourths / total_time_spent) * 100
        
        # Calculate the midpoints of each third
        #fourth_midpoints = [pitch_length / 8, pitch_length * 3 / 8, pitch_length * 5 / 8, pitch_length * 7 / 8]
            
        pitch = VerticalPitch(pitch_type='custom',  # example plotting a tracab pitch
                      pitch_length=pitch_length_meters, pitch_width=pitch_width_meters,
                      axis=False, label=False)  # showing axis labels is optional
        fig, ax = pitch.draw()
        
        percentage_increase_lat = ((top_right_lat - top_left_lat) / top_left_lat) * 100
        
        # plotting third percentages
        #for midpoint, percentage, label in zip(fourth_midpoints, percentage_time_in_fourths, percentage_time_in_fourths.index):
        #    ax.text(pitch_width_meters / 2, midpoint, f'{label}\n{int(round(percentage))}%', ha='center', va='center', fontsize=11, weight='bold')
        
        if (top_left_lat < bottom_left_lat) | (top_left_lat < bottom_right_lat) | (percentage_increase_lat > 0.0005):
            swap_condition = lat_long_filtered['timestamp'] > lat_long_filtered['period_2_start_time']
            lat_long_filtered.loc[swap_condition, 'x'] = pitch_width_meters - lat_long_filtered.loc[swap_condition, 'x']
            lat_long_filtered.loc[swap_condition, 'y'] = pitch_length_meters - lat_long_filtered.loc[swap_condition, 'y']
            sns.kdeplot(data=lat_long_filtered, x='x', y='y', ax=ax, cmap='Blues', fill=True, levels=5, alpha=0.9)
        else:
            swap_condition = lat_long_filtered['timestamp'] > lat_long_filtered['period_2_start_time']
            lat_long_filtered.loc[swap_condition, 'y'] = pitch_width_meters - lat_long_filtered.loc[swap_condition, 'y']
            lat_long_filtered.loc[swap_condition, 'x'] = pitch_length_meters - lat_long_filtered.loc[swap_condition, 'x']
            sns.kdeplot(data=lat_long_filtered, x='y', y='x', ax=ax, cmap='Blues', fill=True, levels=5, alpha=0.9)
        
        ax.set_xlim([0, pitch_width_meters])
        ax.set_ylim([pitch_length_meters, 0])
    else:
        pitch = VerticalPitch(pitch_type='custom',  # example plotting a tracab pitch
                      pitch_length=100, pitch_width=70,
                      axis=False, label=False)  # showing axis labels is optional
        fig, ax = pitch.draw()
        
        ax.text(50, 35, 'No heatmap available',
        va='center', ha='center', fontsize=20, color='lightblue', fontweight='bold')
    
    return fig
