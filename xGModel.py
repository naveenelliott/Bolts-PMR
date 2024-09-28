import pandas as pd
import math
import statsmodels.formula.api as smf
import statsmodels.api as sm
import numpy as np


def xGModel(end):
    # getting all the data
    shots = pd.read_csv('xG_historical_data/xGShootingData.csv')
    shots['Goal'] = shots['Event'].str.contains('Goal').astype(int)
    
    headers = pd.read_csv('xG_historical_data/HeadersLogisticRegression.csv')
    headers = headers.drop(['Mins', 'Secs', 'Team', 'Event'], axis=1)
    wyscout = pd.read_csv('xG_historical_data/WyscoutHeadersFurther.csv')
    wyscout = wyscout.drop(['subEventName'], axis=1)
    combined_df_headers = pd.concat([headers, wyscout])
    combined_df_headers['Player'] = 'Header'
    
    headers = pd.read_csv('xG_historical_data/FreeKicksLogisticRegression.csv')
    headers = headers.drop(['Mins', 'Secs', 'Team', 'Event'], axis=1)
    wyscout = pd.read_csv('xG_historical_data/WyscoutFreeKicks.csv')
    wyscout = wyscout.drop(['subEventName', 'positions'], axis=1)
    statsbomb = pd.read_csv('xG_historical_data/StatsBombFreeKicks.csv')
    combined_df_fk = pd.concat([headers, wyscout, statsbomb])
    combined_df_fk['Player'] = 'FK'
    
    # Functions to get distance and angle
    def distance(point1, point2):
        return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
    
    def angle_between_points(shot_point, post1, post2):
        # Calculate the distances between the points
        a = distance(shot_point, post1)
        b = distance(shot_point, post2)
        c = distance(post1, post2)
        
        # Use law of cosines to find the angle
        angle_radians = math.acos((a**2 + b**2 - c**2) / (2 * a * b))
        
        # Convert radians to degrees
        angle_degrees = math.degrees(angle_radians)
        
        return angle_degrees
    
    # Function to calculate angle for each row
    def calculate_angle(row):
        shot_point = (row['X'], row['Y'])
        post1 = (100, 46.34)  # Assuming the first row is the shot point
        post2 = (100, 53.36)  # Assuming the second and third rows are the posts
        return angle_between_points(shot_point, post1, post2)
    
    def calculate_distance(row):
        shot_point = (row['X'], row['Y'])
        post1 = (100, 50)  # Assuming the first row is the shot point
        return distance(shot_point, post1)
    
    # Apply the function to create a new column with angles
    shots['Angle'] = shots.apply(calculate_angle, axis=1)
    shots['Distance'] = shots.apply(calculate_distance, axis=1)
    
    end['Angle'] = end.apply(calculate_angle, axis=1)
    end['Distance'] = end.apply(calculate_distance, axis=1)
    
    shots.drop(columns=['Event', 'Unnamed: 0', 'Event', 'Team'], inplace=True)
    
    shots = pd.concat([shots, combined_df_fk, combined_df_headers], ignore_index=True)
    
    condition = shots['Player'] == 'Penalty'
    pens = shots[condition]
    shots = shots[~condition].reset_index(drop=True)
    pens = pens.reset_index(drop=True)
    pens['xG'] = 0.75
    
    test_model = smf.glm(formula="Goal ~ Angle + Distance + Player", data=shots, 
                               family=sm.families.Binomial()).fit()
    # Seeing the coefficient and p-values, I know the Angle isn't that significant 
    # but it is for a large sample size
    
    print(test_model.summary())   
    b=test_model.params
    model_variables = ['Angle','Distance', 'Player']
    
    player_dummies = pd.get_dummies(shots['Player'], drop_first=True).columns
    
    # Return xG value, for each point
    def calculate_xG(sh):    
       bsum=b[0]
       for var in model_variables:
            if var == 'Player':
                player_name = sh[var]
                if player_name in player_dummies:
                    bsum += b[f'Player[T.{player_name}]']
            else:
                bsum += b[var] * sh[var]
       xG = 1 / (1 + np.exp(-bsum))
       return xG
    
    
    #Add an xG to my dataframe
    xG=end.apply(calculate_xG, axis=1)
    end = end.assign(xG=xG)
    
    end = pd.concat([end, pens], ignore_index=True)
    
    def time_to_seconds(time_str):
        minutes, seconds = map(int, time_str.split(':'))
        return minutes + (seconds/60)
    
    # Apply the function to the 'Time' column
    end['Time'] = end['Time'].apply(time_to_seconds)
    end = end.drop(columns=['Angle', 'Distance', 'Goal', 'Mins', 'Secs', 'X2', 'Y2'])
    return end
