import streamlit as st
import pandas as pd
from GettingFullActions import UpdatingActions
from GettingPSDLineupData import getting_PSD_lineup_data

# Setting the title of the PMR App in web browser
st.set_page_config(page_title='Bolts Post-Match Review App', page_icon = 'PostMatchReviewApp_v2/pages/Boston_Bolts.png')


st.sidebar.success('Select a page above.')

# this updates actions
combined_actions = UpdatingActions()

# these are the allowable teams that we have event data for
bolts_allowed = pd.Series(combined_actions['Team'].unique())
opp_allowed = pd.Series(combined_actions['Opposition'].unique())
combined_actions['Match Date'] = pd.to_datetime(combined_actions['Match Date']).dt.strftime('%m/%d/%Y')
date_allowed = pd.Series(combined_actions['Match Date'].unique())
combined_actions['Match Identifier'] = combined_actions['Team'] + ' vs ' + combined_actions['Opposition'] + ' on ' + combined_actions['Match Date'].astype(str)
unique_match_identifiers = combined_actions['Match Identifier'].drop_duplicates().reset_index(drop=True)
st.session_state['match_identifiers'] = unique_match_identifiers



combined_df = getting_PSD_lineup_data()
combined_df['Starts'] = combined_df['Starts'].astype(float)
combined_df['Date'] = pd.to_datetime(combined_df['Date'])
combined_df['Date'] = combined_df['Date'].dt.strftime('%m/%d/%Y')

combined_df = combined_df.loc[combined_df['Team Name'].isin(bolts_allowed) & combined_df['Opposition'].isin(opp_allowed)].reset_index(drop=True)

combined_df.loc[combined_df['Player Full Name'] == 'Casey Powers', 'Position Tag'] = 'GK'
gk_dataframe = combined_df.loc[combined_df['Position Tag'] == 'GK'].reset_index(drop=True)
in_and_out_goals_gk = pd.read_csv('PostMatchReviewApp_v4/pages/InAndOutOfPossessionGoalsGK.csv')
gk_dataframe = pd.merge(gk_dataframe, in_and_out_goals_gk, on=['Team Name', 'Opposition', 'Date', 'Player Full Name'], how='outer')
gk_dataframe = gk_dataframe.drop_duplicates().reset_index(drop=True)
st.session_state['complete_gk_df'] = gk_dataframe.copy()


# THIS IS THE NEW STUFF, SHOULD BE IN VERSION 3
in_and_out_goals = pd.read_csv('PostMatchReviewApp_v4/pages/InAndOutOfPossessionGoals.csv')
combined_df = pd.merge(combined_df, in_and_out_goals, on=['Team Name', 'Opposition', 'Date'], how='inner')
combined_df = combined_df.drop_duplicates().reset_index(drop=True)

# creating a transferrable copy of the combined dataset
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

# TEMPORARY
gk_dataframe = combined_df.loc[combined_df['Position Tag'] == 'GK'].reset_index(drop=True)
st.session_state['gk_df'] = gk_dataframe