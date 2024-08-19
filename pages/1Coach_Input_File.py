import streamlit as st
import pandas as pd

# Getting the selected team, opponent, and date
selected_team = st.session_state["selected_team"]
selected_opp = st.session_state["selected_opp"]
selected_date = st.session_state["selected_date"]

st.set_page_config(layout='wide')

# Function that will save the input
def save_input(in_possession, out_possession, veo_hyperlink, competition_level):

    overall = st.session_state['overall_df']
    overall.loc[overall['Player Full Name'] == 'Casey Powers', 'Position Tag'] = 'GK'
    condition = (
        (overall['Team Name'] == st.session_state['selected_team']) &
        (overall['Opposition'] == st.session_state['selected_opp']) &
        (overall['Date'] == st.session_state['selected_date'])
    )
    overall.loc[condition, 'In Possession'] = in_possession
    overall.loc[condition, 'Out Possession'] = out_possession
    overall.loc[condition, 'Veo Hyperlink'] = veo_hyperlink
    overall.loc[condition, 'Competition Level'] = competition_level

    limited_df = overall[['Team Name', 'Date', 'Opposition', 'In Possession', 'Out Possession', 'Veo Hyperlink', 'Competition Level']]
    limited_df.to_csv('PostMatchReviewApp_v4/pages/InAndOutOfPossessionGoals.csv', index=False)
    st.session_state['overall_df'] = overall

def main():
    st.title("Setting In and Out of Possession Goals")

    st.markdown(f"<h3 style='text-align: center;'>Team: {selected_team}&nbsp;|&nbsp;Opposition: {selected_opp}</h3>", unsafe_allow_html=True)

    # Display current DataFrame
    overall = st.session_state['overall_df']
    condition = (
        (overall['Team Name'] == st.session_state['selected_team']) &
        (overall['Opposition'] == st.session_state['selected_opp']) &
        (overall['Date'] == st.session_state['selected_date'])
    )
    overall = overall.loc[condition]
    current_in_possession = overall.iloc[0]['In Possession']
    current_out_possession = overall.iloc[0]['Out Possession']
    current_veo_hyperlink = overall.iloc[0]['Veo Hyperlink'] if 'Veo Hyperlink' in overall.columns else ''
    current_competition_level = overall.iloc[0]['Competition Level'] if 'Competition Level' in overall.columns else ''

    if pd.isna(current_in_possession):
        current_in_possession = 'Nothing, needs updated.'
    if pd.isna(current_out_possession):
        current_out_possession = 'Nothing, needs updated.'

    st.write(f"In Possession Current Goals: {current_in_possession}")
    st.write(f"Out Possession Current Goals: {current_out_possession}")
    st.write(f"Veo Hyperlink: {current_veo_hyperlink}")
    st.write(f"Competition Level: {current_competition_level}")

    # Form to update the DataFrame
    with st.form("input_form"):
        in_possession = st.text_input("In Possession:")
        out_possession = st.text_input("Out of Possession:")
        veo_hyperlink = st.text_input("Veo Hyperlink:", value=current_veo_hyperlink)
        competition_level = st.text_input("Competition Level:", value=current_competition_level)
        submit_button = st.form_submit_button(label='Save')

        if submit_button:
            save_input(in_possession, out_possession, veo_hyperlink, competition_level)
            st.success("Input updated!")

if __name__ == "__main__":
    main()
