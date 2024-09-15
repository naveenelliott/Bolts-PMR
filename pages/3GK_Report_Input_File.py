import streamlit as st
import pandas as pd
import numpy as np
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title='Bolts Post-Match Review App', page_icon='pages/Boston_Bolts.png')

st.title("Goalkeeper Report Input File")

gk_data = st.session_state['gk_df']
gks = list(gk_data['Player Full Name'].unique())
if "selected_gk" not in st.session_state:
    st.session_state["selected_gk"] = gks[0] 
selected_gk = st.selectbox('Choose the Goalkeeper:', gks)
st.session_state["selected_gk"] = selected_gk


selected_opp = st.session_state['selected_opp']
st.markdown(f"<h3 style='text-align: left;'>{selected_opp} Goalkeeper Report</h3>", unsafe_allow_html=True)
selected_team = st.session_state['selected_team']
selected_date = st.session_state['selected_date']

# Establishing a Google Sheets connection
conn = st.connection('gsheets', type=GSheetsConnection)

existing_data = conn.read(worksheet='GK_Report', ttl=0)
existing_data.dropna(how='all', inplace=True)
existing_data['Bolts Team'] = existing_data['Bolts Team'].fillna('').astype(str)
existing_data['Opposition'] = existing_data['Opposition'].fillna('').astype(str)
existing_data['Match Date'] = existing_data['Match Date'].fillna('').astype(str)
existing_data['GK Name'] = existing_data['GK Name'].fillna('').astype(str)

# Initialize variables for form display
in_possession, out_possession, veo_hyperlink, coach_notes = '', '', '', ''

updated_df = pd.DataFrame()

# Check if the selected match data already exists
if (existing_data['Bolts Team'].str.contains(selected_team).any() & 
    existing_data['Opposition'].str.contains(selected_opp).any() & 
    existing_data['Match Date'].str.contains(selected_date).any() &
    existing_data['GK Name'].str.contains(selected_gk).any()):

    index = existing_data[
        (existing_data['Bolts Team'] == selected_team) &
        (existing_data['Opposition'] == selected_opp) &
        (existing_data['Match Date'] == selected_date) &
        (existing_data['GK Name'] == selected_gk)
    ].index

    updated_df = existing_data.copy()
    
    if not index.empty:
        # Extract existing data to display
        in_possession = existing_data.loc[index, 'In Possession Goals'].values[0]
        out_possession = existing_data.loc[index, 'Out of Possession Goals'].values[0]
        coach_notes = existing_data.loc[index, 'Coach Notes'].values[0]
        veo_hyperlink = existing_data.loc[index, 'Veo Hyperlink'].values[0]

# Form to update the DataFrame
with st.form("input_form"):
    in_possession = st.text_input("In Possession:", value=in_possession)
    out_possession = st.text_input("Out of Possession:", value=out_possession)
    veo_hyperlink = st.text_input("Veo Hyperlink:", value=veo_hyperlink)
    coach_notes = st.text_input("Coach Notes:", value=coach_notes)
    submit_button = st.form_submit_button(label='Save')

    if submit_button:
        # Ensure all fields are filled
        if not in_possession or not out_possession or not veo_hyperlink or not coach_notes:
            st.warning('Ensure all fields are filled')
            st.stop()
        
        # Update existing data if match data exists
        if (existing_data['Bolts Team'].str.contains(selected_team).any() & existing_data['Opposition'].str.contains(selected_opp).any() & 
            existing_data['Match Date'].str.contains(selected_date).any() & existing_data['GK Name'].str.contains(selected_gk).any()):
            existing_data.loc[index, 'In Possession Goals'] = in_possession
            existing_data.loc[index, 'Out of Possession Goals'] = out_possession
            existing_data.loc[index, 'Veo Hyperlink'] = veo_hyperlink
            existing_data.loc[index, 'Coach Notes'] = coach_notes
            updated_df = existing_data.copy()
        else:
            # Add new data if match data does not exist
            new_data = pd.DataFrame([{
                'Bolts Team': selected_team,
                'Opposition': selected_opp,
                'Match Date': selected_date,
                'GK Name': selected_gk,
                'In Possession Goals': in_possession, 
                'Out of Possession Goals': out_possession,
                'Veo Hyperlink': veo_hyperlink,
                'Coach Notes': coach_notes
            }])
            updated_df = pd.concat([existing_data, new_data], ignore_index=True)
        
        # Update the Google Sheet
        conn.update(worksheet='GK_Report', data=updated_df)
        st.success("Input updated!")
        st.rerun()  # Rerun to refresh the displayed DataFrame

st.write(f"In Possession Current Goals: {in_possession}")
st.write(f"Out Possession Current Goals: {out_possession}")
st.write(f"Veo Hyperlink: {veo_hyperlink}")
st.write(f"Competition Level: {coach_notes}")

