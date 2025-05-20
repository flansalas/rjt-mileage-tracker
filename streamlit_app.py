import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="RJT Mileage Tracker", page_icon="🚗")

st.title("🚗 RJT Mileage Logger")

# Input form
with st.form("log_trip"):
    trip_date = st.date_input("Date", value=date.today())
    driver = st.text_input("Driver Name")
    job = st.text_input("Job or Client")
    odo_start = st.number_input("Odometer Start", min_value=0)
    odo_end = st.number_input("Odometer End", min_value=0)
    rate = 0.67
    notes = st.text_area("Notes", "")

    submitted = st.form_submit_button("Submit Trip")

if submitted:
    miles = round(odo_end - odo_start, 2)
    reimbursement = round(miles * rate, 2)
    
    new_data = {
        "Date": [trip_date],
        "Driver": [driver],
        "Job": [job],
        "Odo Start": [odo_start],
        "Odo End": [odo_end],
        "Miles": [miles],
        "Reimbursement": [reimbursement],
        "Notes": [notes]
    }

    df_new = pd.DataFrame(new_data)

    # Load or create trip log CSV
    try:
        df = pd.read_csv("trip_log.csv")
        df = pd.concat([df, df_new], ignore_index=True)
    except FileNotFoundError:
        df = df_new

    df.to_csv("trip_log.csv", index=False)

    st.success(f"Trip logged! {miles} miles – ${reimbursement:.2f}")

# Display trip log
st.subheader("📋 Trip History")
try:
    df = pd.read_csv("trip_log.csv")
    st.dataframe(df)
except FileNotFoundError:
    st.info("No trips logged yet.")
