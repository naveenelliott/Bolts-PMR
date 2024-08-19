import streamlit as st
import pandas as pd
import numpy as np


def save_input(in_possession, out_possession, coach_notes, veo_hyperlink):

    overall_gk = st.session_state['complete_gk_df']
    condition = (
        (overall_gk['Team Name'] == st.session_state['selected_team']) &
        (overall_gk['Opposition'] == st.session_state['selected_opp']) &
        (overall_gk['Date'] == st.session_state['selected_date']) &
        (overall_gk['Player Full Name'] == st.session_state['selected_gk'])
    )
    overall_gk.loc[condition, 'In Possession'] = in_possession
    overall_gk.loc[condition, 'Out Possession'] = out_possession
    overall_gk.loc[condition, 'Vasily Notes'] = coach_notes
    overall_gk.loc[condition, 'Veo Hyperlink GK'] = veo_hyperlink
    limited_df_gk = overall_gk[['Player Full Name', 'Team Name', 'Date', 'Opposition', 'In Possession', 'Out Possession', 'Vasily Notes', 'Veo Hyperlink GK']]
    limited_df_gk.to_csv('PostMatchReviewApp_v4/pages/InAndOutOfPossessionGoalsGK.csv', index=False)
    st.session_state['complete_gk_df'] = overall_gk

def main():
    st.title("Goalkeeper Report Input File")

    gk_data = st.session_state['gk_df']

    gks = list(gk_data['Player Full Name'].unique())
    if "selected_gk" not in st.session_state:
        st.session_state["selected_gk"] = gks[0] 
    selected_gk = st.selectbox('Choose the Goalkeeper:', gks)
    st.session_state["selected_gk"] = selected_gk


    opponent = st.session_state['selected_opp']
    st.markdown(f"<h3 style='text-align: left;'>{opponent} Goalkeeper Report</h3>", unsafe_allow_html=True)

    in_and_out_goals = pd.read_csv('PostMatchReviewApp_v4/pages/InAndOutOfPossessionGoalsGK.csv')

    condition = (
    (in_and_out_goals['Team Name'] == st.session_state['selected_team']) &
    (in_and_out_goals['Opposition'] == st.session_state['selected_opp']) &
    (in_and_out_goals['Date'] == st.session_state['selected_date']) &
    (in_and_out_goals['Player Full Name'] == st.session_state['selected_gk'])
    )

    if condition.any():
        row = in_and_out_goals.loc[condition].iloc[0]  # Get the first matching row
        in_possession_display = row['In Possession'] if not pd.isna(row['In Possession']) else 'Nothing, needs updated.'
        out_possession_display = row['Out Possession'] if not pd.isna(row['Out Possession']) else 'Nothing, needs updated.'
        coach_notes_display = row['Vasily Notes'] if not pd.isna(row['Vasily Notes']) else 'Nothing, needs updated.'
        veo_hyperlink_display = row['Veo Hyperlink GK'] if not pd.isna(row['Veo Hyperlink GK']) else 'Nothing, needs updated.'
    else:
        in_possession_display = 'Nothing, needs updated.'
        out_possession_display = 'Nothing, needs updated.'
        coach_notes_display = 'Nothing, needs updated.'
        veo_hyperlink_display = 'Nothing, needs updated.'


    st.write(f"In Possession Current Goals: {in_possession_display}")
    st.write(f"Out Possession Current Goals: {out_possession_display}")
    st.write(f"Current Coach Notes: {coach_notes_display}")
    st.write(f"Current Veo Hyperlink: {veo_hyperlink_display}")

    # Form to update the DataFrame
    with st.form("input_form"):
        in_possession_goals = st.text_input("In Possession GK Game Plan:")
        out_possession_goals = st.text_input("Out of Possession GK Game Plan:")
        coach_notes_input = st.text_input('Enter Coach Notes Here:')
        veo_hyperlink_input = st.text_input('Enter Veo Hyperlink Here:')
        
        submit_button = st.form_submit_button(label='Save')

        if submit_button:
            save_input(in_possession=in_possession_goals, out_possession=out_possession_goals, coach_notes=coach_notes_input, 
                       veo_hyperlink=veo_hyperlink_input)
            st.success("Input updated!")

if __name__ == "__main__":
    main()
