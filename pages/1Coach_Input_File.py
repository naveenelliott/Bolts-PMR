import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Getting the selected team, opponent, and date
selected_team = st.session_state.get("selected_team")
selected_opp = st.session_state.get("selected_opp")
selected_date = st.session_state.get("selected_date")


st.set_page_config(layout='wide', page_title='Bolts Post-Match Review App', page_icon='pages/Boston_Bolts.png')

# Establishing a Google Sheets connection
conn = st.connection('gsheets', type=GSheetsConnection)

existing_data = conn.read(worksheet='PMR', ttl=0)
existing_data.dropna(how='all', inplace=True)
existing_data['Bolts Team'] = existing_data['Bolts Team'].fillna('').astype(str)
existing_data['Opposition'] = existing_data['Opposition'].fillna('').astype(str)
existing_data['Match Date'] = existing_data['Match Date'].fillna('').astype(str)

# Initialize variables for form display
in_possession, out_possession, veo_hyperlink, competition_level = '', '', '', ''

updated_df = pd.DataFrame()

# Check if the selected match data already exists
match_exists = (
    existing_data['Bolts Team'].str.contains(selected_team).any() & 
    existing_data['Opposition'].str.contains(selected_opp).any() & 
    existing_data['Match Date'].str.contains(selected_date).any()
)

if match_exists:
    index = existing_data[
        (existing_data['Bolts Team'] == selected_team) &
        (existing_data['Opposition'] == selected_opp) &
        (existing_data['Match Date'] == selected_date)
    ].index

    updated_df = existing_data.copy()

    # Extract existing data to display
    if not index.empty:
        in_possession = existing_data.loc[index, 'In Possession Goals'].values[0]
        out_possession = existing_data.loc[index, 'Out of Possession Goals'].values[0]
        veo_hyperlink = existing_data.loc[index, 'Veo Hyperlink'].values[0]
        competition_level = existing_data.loc[index, 'Competition Level'].values[0]

st.title("Setting In and Out of Possession Goals")

st.markdown(f"<h3 style='text-align: center;'>Team: {selected_team}&nbsp;|&nbsp;Opposition: {selected_opp}</h3>", unsafe_allow_html=True)

# Form to update the DataFrame
with st.form("input_form"):
    in_possession = st.text_input("In Possession:", value=in_possession)
    out_possession = st.text_input("Out of Possession:", value=out_possession)
    veo_hyperlink = st.text_input("Veo Hyperlink:", value=veo_hyperlink)
    competition_level = st.text_input("Competition Level:", value=competition_level)
    submit_button = st.form_submit_button(label='Save')

    if submit_button:
        # Ensure all fields are filled
        if not in_possession or not out_possession or not veo_hyperlink or not competition_level:
            st.warning('Ensure all fields are filled')
            st.stop()
        
        # Update existing data if match data exists
        if match_exists and not index.empty:
            existing_data.loc[index, 'In Possession Goals'] = in_possession
            existing_data.loc[index, 'Out of Possession Goals'] = out_possession
            existing_data.loc[index, 'Veo Hyperlink'] = veo_hyperlink
            existing_data.loc[index, 'Competition Level'] = competition_level
            updated_df = existing_data.copy()
        else:
            # Add new data if match data does not exist
            new_data = pd.DataFrame([{
                'Bolts Team': selected_team,
                'Opposition': selected_opp,
                'Match Date': selected_date,
                'In Possession Goals': in_possession, 
                'Out of Possession Goals': out_possession,
                'Veo Hyperlink': veo_hyperlink,
                'Competition Level': competition_level
            }])
            updated_df = pd.concat([existing_data, new_data], ignore_index=True)
        
        # Update the Google Sheet
        conn.update(worksheet='PMR', data=updated_df)
        st.success("Input updated!")
        st.rerun()  # Rerun to refresh the displayed DataFrame

st.write(f"In Possession Current Goals: {in_possession}")
st.write(f"Out Possession Current Goals: {out_possession}")
st.write(f"Veo Hyperlink: {veo_hyperlink}")
st.write(f"Competition Level: {competition_level}")
