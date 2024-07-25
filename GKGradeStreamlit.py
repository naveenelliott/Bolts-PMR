import pandas as pd
import numpy as np
from scipy.stats import norm
from datetime import datetime


def GKFunction(dataframe):
    final = pd.DataFrame()
    final['Player Name'] = dataframe['Player Full Name']
    final['Position'] = dataframe['Position Tag']
    final['Final Grade'] = 0
    final['Adjustments'] = 0
    
    return final