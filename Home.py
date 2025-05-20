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

# Show trip history (for all users)
try:
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    st.subheader("📋 Trip History")
    st.dataframe(df)

    # Admin-only section
    with st.expander("🔒 GM Admin View"):
        st.markdown("Use the filters below to analyze mileage logs.")

        # Convert date column to datetime
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        # Filters
        unique_drivers = df["Driver"].dropna().unique()
        selected_driver = st.selectbox("Filter by Driver", options=["All"] + list(unique_drivers))
        date_range = st.date_input("Filter by Date Range", [])

        filtered_df = df.copy()

        if selected_driver != "All":
            filtered_df = filtered_df[filtered_df["Driver"] == selected_driver]

        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[(filtered_df["Date"] >= pd.to_datetime(start_date)) & 
                                      (filtered_df["Date"] <= pd.to_datetime(end_date))]

        # Totals
        if not filtered_df.empty:
            total_miles = filtered_df["Miles"].sum()
            total_reimbursement = filtered_df["Reimbursement"].sum()
            st.metric("Total Miles", f"{total_miles:,.2f}")
            st.metric("Total Reimbursement", f"${total_reimbursement:,.2f}")

            # Filtered table
            st.dataframe(filtered_df)

            # Export button
            csv = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download Filtered Data as CSV", data=csv, file_name="filtered_mileage.csv", mime="text/csv")
        else:
            st.info("No data found for the selected filters.")

except Exception as e:
    st.warning("⚠️ Could not load trip history.")
    st.exception(e)
