import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date, datetime
from zoneinfo import ZoneInfo  # ✅ Works on Python 3.9+

st.set_page_config(page_title="RJT Mileage Tracker", page_icon="🚗")
st.title("🚗 RJT Mileage Logger")

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gspread"], scope)
client = gspread.authorize(credentials)

# Open the sheet
sheet = client.open("RJT Mileage Log").worksheet("Trips")

# Form input
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

    # 🕒 Timestamp in Central Time
    central_time = datetime.now(ZoneInfo("America/Chicago"))
    timestamp = central_time.strftime("%b %d, %Y – %I:%M %p")

    row = [str(trip_date), driver, job, odo_start, odo_end, miles, reimbursement, notes, timestamp]
    sheet.append_row(row)
    st.success(f"Trip logged! {miles} miles – ${reimbursement:.2f}")

# Display table
data = sheet.get_all_records()
df = pd.DataFrame(data)
st.subheader("📋 Trip History")
st.dataframe(df)
