import streamlit as st
import pandas as pd
import json
import os

selected_team = st.session_state["selected_team"]
selected_opp = st.session_state["selected_opp"]
selected_date = st.session_state["selected_date"]

st.set_page_config(layout='wide')

# File path for storing the DataFrame
storage_file = 'user_data.json'

def save_input(in_possession, out_possession):
    df = st.session_state['combined_df']
    condition = (
        (df['Team Name'] == st.session_state['selected_team']) &
        (df['Opposition'] == st.session_state['selected_opp']) &
        (df['Date'] == st.session_state['selected_date'])
    )
    df.loc[condition, 'In Possession'] = in_possession
    df.loc[condition, 'Out Possession'] = out_possession
    st.session_state["combined_df"] = df

    overall = st.session_state['overall_df']
    condition = (
        (overall['Team Name'] == st.session_state['selected_team']) &
        (overall['Opposition'] == st.session_state['selected_opp']) &
        (overall['Date'] == st.session_state['selected_date'])
    )
    overall.loc[condition, 'In Possession'] = in_possession
    overall.loc[condition, 'Out Possession'] = out_possession
    # NEED TO FIGURE OUT HOW TO UPDATE THIS FILE

def main():
    st.title("Setting In and Out of Possession Goals")

    # Display current DataFrame
    current_in_possession = st.session_state['combined_df'].iloc[0]['In Possession']
    current_out_possession = st.session_state['combined_df'].iloc[0]['Out Possession']
    if pd.isna(current_in_possession):
        current_in_possession = 'Nothing, needs updated.'
    if pd.isna(current_out_possession):
        current_out_possession = 'Nothing, needs updated.'

    st.write(f"In Possession Current Goals: {current_in_possession}")
    st.write(f"Out Possession Current Goals: {current_out_possession}")

    # Form to update the DataFrame
    with st.form("input_form"):
        in_possession = st.text_input("In Possession:")
        out_possession = st.text_input("Out of Possession:")
        submit_button = st.form_submit_button(label='Save')

        if submit_button:
            save_input(in_possession, out_possession)
            st.success("Input updated!")
            st.experimental_rerun()  # Rerun to refresh the displayed DataFrame

if __name__ == "__main__":
    main()

