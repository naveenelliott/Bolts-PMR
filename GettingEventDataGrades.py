import pandas as pd
import numpy as np
from scipy.stats import norm
from datetime import datetime
import streamlit as st


def calculate_threshold(df, quantile, std_multiplier=2, std_adjustment=0.8):
    end_df = pd.DataFrame(columns=df.columns)
    
    for column in df.columns:
        # HERE IS THE ISSUE
        if df[column].quantile(quantile) < std_multiplier * df[column].std() * std_adjustment:
            threshold = df[column].mean()
        else:
            threshold = df[column].quantile(quantile)
        
        end_df[column] = [threshold]
    
    # Add a row with column standard deviations
    adjusted_std = df.std() * std_adjustment
    end_df.loc[len(end_df)] = adjusted_std
    
    return end_df


def StrikerSOTFunction(select_event_dataframe):

    finishing = select_event_dataframe[['SOT']]
    finishing.fillna(0, inplace=True)

    select_event_dataframe.reset_index(drop=True, inplace=True)
    team_name = select_event_dataframe['Team Name'][0]

    def calculate_percentile(value):
        return norm.cdf(value) * 100

    # Function to calculate z-score for each element in a column
    def calculate_zscore(column, mean, std):
        return (column - mean) / std

    def clip_percentile(value):
        return max(min(value, 100), 50)


    if ('U15' in team_name) or ('U16' in team_name):
        cf_event_df = pd.read_csv("SOT_Thresholds/U15_U16_Thresholds_SOT_ATT.csv")
    else:
        cf_event_df = pd.read_csv("SOT_Thresholds/U17_U19_Thresholds_SOT_ATT.csv")


    mean_values = cf_event_df.iloc[0, 0]
    std_values = cf_event_df.iloc[1, 0]
    z_scores_df = finishing.transform(lambda col: calculate_zscore(col, mean_values, std_values))
    
    if z_scores_df.isna().any().any():
        finishing_percentile = 50
        weights = np.array([0.1])
        finishing_score = finishing_percentile * weights[0]
        final = pd.DataFrame({'Finishing': [finishing_score]})
    else:
        finishing_percentile = z_scores_df.map(calculate_percentile)
        finishing_percentile = finishing_percentile.map(clip_percentile)
        weights = np.array([0.1])
        finishing_score = finishing_percentile * weights[0]
        final = pd.DataFrame()
        final['Finishing'] = finishing_score
        final.reset_index(drop=True, inplace=True)
   
    return final

def WingerSOTFunction(select_event_dataframe):

    finishing = select_event_dataframe[['SOT']]
    finishing.fillna(0, inplace=True)

    select_event_dataframe.reset_index(drop=True, inplace=True)
    team_name = select_event_dataframe['Team Name'][0]

    def calculate_percentile(value):
        return norm.cdf(value) * 100

    # Function to calculate z-score for each element in a column
    def calculate_zscore(column, mean, std):
        return (column - mean) / std

    def clip_percentile(value):
        return max(min(value, 100), 50)


    if ('U15' in team_name) or ('U16' in team_name):
        cf_event_df = pd.read_csv("SOT_Thresholds/U15_U16_Thresholds_SOT_WING.csv")
    else:
        cf_event_df = pd.read_csv("SOT_Thresholds/U17_U19_Thresholds_SOT_WING.csv")


    mean_values = cf_event_df.iloc[0, 0]
    std_values = cf_event_df.iloc[1, 0]
    z_scores_df = finishing.transform(lambda col: calculate_zscore(col, mean_values, std_values))
    
    if z_scores_df.isna().any().any():
        finishing_percentile = 50
        weights = np.array([0.1])
        finishing_score = finishing_percentile * weights[0]
        final = pd.DataFrame({'Finishing': [finishing_score]})
    else:
        finishing_percentile = z_scores_df.map(calculate_percentile)
        finishing_percentile = finishing_percentile.map(clip_percentile)
        weights = np.array([0.1])
        finishing_score = finishing_percentile * weights[0]
        final = pd.DataFrame()
        final['Finishing'] = finishing_score
        final.reset_index(drop=True, inplace=True)
   
    return final

def CMSOTFunction(select_event_dataframe):

    finishing = select_event_dataframe[['SOT']]
    finishing.fillna(0, inplace=True)

    select_event_dataframe.reset_index(drop=True, inplace=True)
    team_name = select_event_dataframe['Team Name'][0]

    def calculate_percentile(value):
        return norm.cdf(value) * 100

    # Function to calculate z-score for each element in a column
    def calculate_zscore(column, mean, std):
        return (column - mean) / std

    def clip_percentile(value):
        return max(min(value, 100), 50)


    if ('U15' in team_name) or ('U16' in team_name):
        cf_event_df = pd.read_csv("SOT_Thresholds/U15_U16_Thresholds_SOT_CM.csv")
    else:
        cf_event_df = pd.read_csv("SOT_Thresholds/U17_U19_Thresholds_SOT_CM.csv")


    mean_values = cf_event_df.iloc[0, 0]
    std_values = cf_event_df.iloc[1, 0]
    z_scores_df = finishing.transform(lambda col: calculate_zscore(col, mean_values, std_values))
    
    if z_scores_df.isna().any().any():
        finishing_percentile = 50
        weights = np.array([0.1])
        finishing_score = finishing_percentile * weights[0]
        final = pd.DataFrame({'Finishing': [finishing_score]})
    else:
        finishing_percentile = z_scores_df.map(calculate_percentile)
        finishing_percentile = finishing_percentile.map(clip_percentile)
        weights = np.array([0.1])
        finishing_score = finishing_percentile * weights[0]
        final = pd.DataFrame()
        final['Finishing'] = finishing_score
        final.reset_index(drop=True, inplace=True)
   
    return final

def StrikerEventFunction(event_dataframe, select_event_dataframe):

    finishing = select_event_dataframe[['xG + xA']]
    finishing.fillna(0, inplace=True)

    select_event_dataframe.reset_index(drop=True, inplace=True)
    team_name = select_event_dataframe['Team'][0]

    def calculate_percentile(value):
        return norm.cdf(value) * 100

    # Function to calculate z-score for each element in a column
    def calculate_zscore(column, mean, std):
        return (column - mean) / std

    def clip_percentile(value):
        return max(min(value, 100), 50)


    if ('U13' in team_name) or ('U14' in team_name):
        cf_event_df = event_dataframe[event_dataframe['Team'].str.contains('U13|U14')]
        del cf_event_df['Team']
        cf_event_df = calculate_threshold(cf_event_df, quantile=0.25, std_multiplier=2)
    elif ('U15' in team_name) or ('U16' in team_name):
        cf_event_df = event_dataframe[event_dataframe['Team'].str.contains('U15|U16')]
        del cf_event_df['Team']
        cf_event_df = calculate_threshold(cf_event_df, quantile=0.25, std_multiplier=2)
    elif ('U17' in team_name) or ('U19' in team_name):
        cf_event_df = event_dataframe[event_dataframe['Team'].str.contains('U17|U19')]
        del cf_event_df['Team']
        cf_event_df = calculate_threshold(cf_event_df, quantile=0.25, std_multiplier=2)


    mean_values = cf_event_df.iloc[0, 0]
    std_values = cf_event_df.iloc[1, 0]
    z_scores_df = finishing.transform(lambda col: calculate_zscore(col, mean_values, std_values))
    
    if z_scores_df.isna().any().any():
        finishing_percentile = 50
        weights = np.array([0.1])
        finishing_score = finishing_percentile * weights[0]
        final = pd.DataFrame({'Finishing': [finishing_score]})
    else:
        finishing_percentile = z_scores_df.map(calculate_percentile)
        finishing_percentile = finishing_percentile.map(clip_percentile)
        weights = np.array([0.1])
        finishing_score = finishing_percentile * weights[0]
        final = pd.DataFrame()
        final['Finishing'] = finishing_score
        final.reset_index(drop=True, inplace=True)
   
    return final

def WingerEventFunction(event_dataframe, select_event_dataframe):

    finishing = select_event_dataframe[['xG + xA']]
    finishing.fillna(0, inplace=True)

    select_event_dataframe.reset_index(drop=True, inplace=True)
    team_name = select_event_dataframe['Team'][0]

    def calculate_percentile(value):
        return norm.cdf(value) * 100

    # Function to calculate z-score for each element in a column
    def calculate_zscore(column, mean, std):
        return (column - mean) / std

    def clip_percentile(value):
        return max(min(value, 100), 50)

    if ('U13' in team_name) or ('U14' in team_name):
        wing_event_df = event_dataframe[event_dataframe['Team'].str.contains('U13|U14')]
        del wing_event_df['Team']
        wing_event_df = calculate_threshold(wing_event_df, quantile=0.25, std_multiplier=2)
    elif ('U15' in team_name) or ('U16' in team_name):
        wing_event_df = event_dataframe[event_dataframe['Team'].str.contains('U15|U16')]
        del wing_event_df['Team']
        wing_event_df = calculate_threshold(wing_event_df, quantile=0.25, std_multiplier=2)
    elif ('U17' in team_name) or ('U19' in team_name):
        wing_event_df = event_dataframe[event_dataframe['Team'].str.contains('U17|U19')]
        del wing_event_df['Team']
        wing_event_df = calculate_threshold(wing_event_df, quantile=0.25, std_multiplier=2)

    mean_values = wing_event_df.iloc[0, 0]
    std_values = wing_event_df.iloc[1, 0]
    z_scores_df = finishing.transform(lambda col: calculate_zscore(col, mean_values, std_values))
    if z_scores_df.isna().any().any():
        finishing_percentile = 50
        weights = np.array([0.1])
        finishing_score = finishing_percentile * weights[0]
        final = pd.DataFrame({'Finishing': [finishing_score]})
    else:
        finishing_percentile = z_scores_df.map(calculate_percentile)
        finishing_percentile = finishing_percentile.map(clip_percentile)
        weights = np.array([0.1])
        finishing_score = finishing_percentile * weights[0]
        final = pd.DataFrame()
        final['Finishing'] = finishing_score
        final.reset_index(drop=True, inplace=True)
        
    return final


def CMEventFunction(event_dataframe, select_event_dataframe):

    playmaking = select_event_dataframe[['xG + xA']]
    playmaking.fillna(0, inplace=True)

    
    select_event_dataframe.reset_index(drop=True, inplace=True)
    team_name = select_event_dataframe['Team'][0]

    def calculate_percentile(value):
        return norm.cdf(value) * 100

    # Function to calculate z-score for each element in a column
    def calculate_zscore(column, mean, std):
        return (column - mean) / std

    def clip_percentile(value):
        return max(min(value, 100), 50)

    if ('U13' in team_name) or ('U14' in team_name):
        cm_event_df = event_dataframe[event_dataframe['Team'].str.contains('U13|U14')]
        del cm_event_df['Team']
        cm_event_df = calculate_threshold(cm_event_df, quantile=0.25, std_multiplier=2)
    elif ('U16' in team_name) or ('U15' in team_name):
        cm_event_df = event_dataframe[event_dataframe['Team'].str.contains('U15|U16')]
        del cm_event_df['Team']
        cm_event_df = calculate_threshold(cm_event_df, quantile=0.25, std_multiplier=2)
    elif ('U17' in team_name) or ('U19' in team_name):
        cm_event_df = event_dataframe[event_dataframe['Team'].str.contains('U17|U19')]
        del cm_event_df['Team']
        cm_event_df = calculate_threshold(cm_event_df, quantile=0.25, std_multiplier=2)

    
    mean_values = cm_event_df.iloc[0, 0]
    std_values = cm_event_df.iloc[1, 0]
    z_scores_df = playmaking.transform(lambda col: calculate_zscore(col, mean_values, std_values))
    if z_scores_df.isna().any().any():
        playmaking_percentile = 50
        weights = np.array([0.1])
        playmaking_score = playmaking_percentile * weights[0]
        final = pd.DataFrame({'Playmaking': [playmaking_score]})
    else:
        playmaking_percentile = z_scores_df.map(calculate_percentile)
        playmaking_percentile = playmaking_percentile.map(clip_percentile)
        weights = np.array([0.1])
        playmaking_score = playmaking_percentile * weights[0]
        final = pd.DataFrame()
        final['Playmaking'] = playmaking_score
        final.reset_index(drop=True, inplace=True)

    
    return final
