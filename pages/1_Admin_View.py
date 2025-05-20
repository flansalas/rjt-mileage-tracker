import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Admin View", page_icon="🧮")

st.title("🧮 GM Admin Dashboard")

# Auth
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gspread"], scope)
client = gspread.authorize(credentials)
sheet = client.open("RJT Mileage Log").worksheet("Trips")

# Load data
data = sheet.get_all_records()
df = pd.DataFrame(data)

# Filters
with st.sidebar:
    st.header("🔍 Filters")
    driver_filter = st.multiselect("Driver", options=df["Driver"].unique(), default=df["Driver"].unique())
    date_range = st.date_input("Date range", [])
    job_filter = st.text_input("Job or Client (optional)")

# Apply filters
if driver_filter:
    df = df[df["Driver"].isin(driver_filter)]

if len(date_range) == 2:
    df["Date"] = pd.to_datetime(df["Date"])
    df = df[(df["Date"] >= pd.to_datetime(date_range[0])) & (df["Date"] <= pd.to_datetime(date_range[1]))]

if job_filter:
    df = df[df["Job"].astype(str).str.contains(job_filter, case=False)]

# Summary
st.subheader("📊 Totals")
st.write(f"**Total Miles:** {df['Miles'].sum():,.2f}")
st.write(f"**Total Reimbursement:** ${df['Reimbursement'].sum():,.2f}")

# Display filtered table
st.subheader("📋 Filtered Trip Log")
st.dataframe(df)

# Download
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download CSV", csv, "filtered_trip_log.csv", "text/csv")
