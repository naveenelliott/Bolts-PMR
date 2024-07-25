import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import Pitch, VerticalPitch
from matplotlib.offsetbox import OffsetImage
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Circle
from highlight_text import fig_text
import numpy as np
from FBGradeStreamlit import FBFunction
from CBGradeStreamlit import CBFunction
from CDMGradeStreamlit import CDMFunction
from CMGradeStreamlit import CMFunction
from WingerGradeStreamlit import WingerFunction
from StrikerGradeStreamlit import StrikerFunction
from GKGradeStreamlit import GKFunction
from fuzzywuzzy import process
from GettingFullActions import UpdatingActions
from GettingPSDLineupData import getting_PSD_lineup_data

st.set_page_config(page_title='Bolts Post-Match Review App')

st.sidebar.success('Select a page above.')

combined_actions = UpdatingActions()

bolts_allowed = pd.Series(combined_actions['Team'].unique())
opp_allowed = pd.Series(combined_actions['Opposition'].unique())

combined_df = getting_PSD_lineup_data()
combined_df['Starts'] = combined_df['Starts'].astype(float)
combined_df['Date'] = pd.to_datetime(combined_df['Date'])
combined_df['Date'] = combined_df['Date'].dt.strftime('%m/%d/%Y')

combined_df = combined_df.loc[combined_df['Team Name'].isin(bolts_allowed) & combined_df['Opposition'].isin(opp_allowed)].reset_index(drop=True)
combined_df['In Possession'] = ''
combined_df['Out Possession'] = ''

st.session_state['overall_df'] = combined_df.copy()

st.title("Bolts Post-Match Review App")

st.markdown("Select the Team, Opponent, and Date (Optional) to See the Post-Match Review")

teams = list(combined_df['Team Name'].unique())
teams.sort()
if "selected_team" not in st.session_state:
    st.session_state['selected_team'] = teams[0]
selected_team = st.selectbox('Choose the Bolts MLS Next Team:', teams, index=teams.index(st.session_state['selected_team']))
combined_df = combined_df.loc[combined_df['Team Name'] == selected_team]

opps = list(combined_df['Opposition'].unique())
if "selected_opp" not in st.session_state:
    st.session_state["selected_opp"] = opps[0] 
selected_opp = st.selectbox('Choose the Opposition:', opps, index=opps.index(st.session_state["selected_opp"]))
combined_df = combined_df.loc[combined_df['Opposition'] == selected_opp]

combined_df['Date'] = pd.to_datetime(combined_df['Date'])
combined_df['Date'] = combined_df['Date'].dt.strftime('%m/%d/%Y')
date = list(combined_df['Date'].unique())
if 'date' not in st.session_state:
    st.session_state['selected_date'] = date[0]
selected_date = st.selectbox('Choose the Date (if necessary)', date, index=date.index(st.session_state['selected_date']))
combined_df = combined_df.loc[combined_df['Date'] == selected_date]

# Initialize prev_player in session state if not already present

st.session_state["combined_df"] = combined_df
combined_df_copy = combined_df.copy()
st.session_state['combined_df_copy'] = combined_df_copy
st.session_state["selected_team"] = selected_team
st.session_state["selected_opp"] = selected_opp
st.session_state["selected_date"] = selected_date