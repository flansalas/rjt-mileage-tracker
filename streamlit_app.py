import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# Set up page
st.set_page_config(page_title="RJT Mileage Tracker", page_icon="🚗")
st.title("🚗 RJT Mileage Logger")

# Google Sheets connection
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gspread"], scope)
client = gspread.authorize(credentials)
sheet = client.open("RJT Mileage Log").worksheet("Trips")

# Form UI
with st.form("log_trip"):
    st.subheader("📝 Log a New Trip")

    trip_date = st.date_input("Date", value=date.today())
    driver = st.text_input("Driver Name")
    job = st.text_input("Job or Client")
    odo_start = st.number_input("Odometer Start", min_value=0)
    odo_end = st.number_input("Odometer End", min_value=0)
    notes = st.text_area("Notes", "")

    submitted = st.form_submit_button("Submit Trip")

# Submission logic
if submitted:
    # Basic validation
    if not driver or not job:
        st.error("Please enter both Driver Name and Job/Client.")
    elif odo_end <= odo_start:
        st.error("Odometer End must be greater than Start.")
    else:
        miles = round(odo_end - odo_start, 2)
        rate = 0.67
        reimbursement = round(miles * rate, 2)

        row = [str(trip_date), driver, job, odo_start, odo_end, miles, reimbursement, notes]

        try:
            sheet.append_row(row)
            st.success(f"✅ Trip logged for {driver}: {miles} miles – ${reimbursement:.2f}")
        except Exception as e:
            st.error("Failed to log trip. Please try again or contact admin.")
            st.exception(e)

# Show trip history
try:
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    st.subheader("📋 Trip History")
    st.dataframe(df)
except Exception as e:
    st.warning("⚠️ Could not load trip history.")
    st.exception(e)
