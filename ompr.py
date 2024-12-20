import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from sklearn.linear_model import LinearRegression
import numpy as np
import random

# Excel file paths
EXCEL_BILLS = "monthly_bills.xlsx"
EXCEL_APPLIANCE_DATA = "appliance_data.xlsx"

def clear_data():
    try:
        # Clear the content in the Excel files by resetting them to empty DataFrames with the same columns
        bills_df = pd.DataFrame(columns=["Month", "Category", "Amount", "Description", "Type", "Service Number"])
        appliance_data_df = pd.DataFrame(columns=["Item", "Kilovolts (kV)", "Start Time", "Max Limit (kV)", "Total Volts", "Email"])
        
        # Save the empty DataFrames back to the Excel files
        bills_df.to_excel(EXCEL_BILLS, index=False)
        appliance_data_df.to_excel(EXCEL_APPLIANCE_DATA, index=False)

        st.success("Present Bills Data is cleared successfully!")
    except Exception as e:
        st.error(f"Error clearing data: {e}")
# Function to send an email
def send_email(subject, body, receiver_email):
    sender_email = "v647414@gmail.com"  # Replace with your email
    sender_password = "kmmz ktrc tgnt ovvf"  # Replace with your App Password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            st.success(f"Email alert sent successfully to {receiver_email}!")
    except Exception as e:
        st.error(f"Error sending email: {e}")

# Function to initialize Excel files
def initialize_excel(file, columns):
    try:
        return pd.read_excel(file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=columns)
        df.to_excel(file, index=False)
        return df

# Initialize files
bills_df = initialize_excel(EXCEL_BILLS, ["Month", "Category", "Amount", "Description", "Type", "Service Number"])
appliance_data_df = initialize_excel(EXCEL_APPLIANCE_DATA, ["Item", "Kilovolts (kV)", "Start Time", "Max Limit (kV)", "Total Volts", "Email"])

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Data Entry for Bills", "Graphical Reports", "Appliance Voltage Monitoring", "Electricity Bill Prediction","Clear Data"])

# ---- DATA ENTRY SECTION ----
# Initial meter reading
initial_meter_reading = 16932

# Function to generate bill data for Household
def generate_household_bill_data(service_number):
    current_month = datetime.now().month
    months = list(range(1, current_month))  # From January to just before current month

    monthly_data = []
    meter_reading = initial_meter_reading

    for month in months:
        random_number = meter_reading+random.randint(80, 150)
        new_reading = random_number-meter_reading  # Subtract the random number
        bill_amount = abs(new_reading * 1.50)  # Multiply the difference by ₹1.50 for Household

        meter_reading = new_reading

        monthly_data.append({
            "Month": month,
            "Category": "Electricity",
            "Amount": round(bill_amount, 2),
            "Description": f"Electricity bill for Household for Month {month}",
            "Type": "Household",
            "Service Number": service_number
        })

    return monthly_data

# Function to generate bill data for Business
def generate_business_bill_data(service_number):
    current_month = datetime.now().month
    months = list(range(1, current_month))  # From January to just before current month

    monthly_data = []
    meter_reading = initial_meter_reading

    for month in months:
        random_number = meter_reading+random.randint(250, 400)
        new_reading = random_number-meter_reading  # Subtract the random number
        bill_amount = abs(new_reading * 2.50)  # Multiply the difference by ₹1.50 for Household

        meter_reading = new_reading


        monthly_data.append({
            "Month": month,
            "Category": "Electricity",
            "Amount": round(bill_amount, 2),
            "Description": f"Electricity bill for Business for Month {month}",
            "Type": "Business",
            "Service Number": service_number
        })

    return monthly_data
flagb=0
flagh=0
# ---- DATA ENTRY SECTION ----
if page == "Data Entry for Bills":
    service_number = st.text_input("Enter Service Number", placeholder="Enter service number")
    connection_type = st.selectbox("Connection Type", ["Household", "Business"])
    if st.button("Get Bill Data"):
        if service_number:
            try:
                bills_df = pd.read_excel(EXCEL_BILLS)
            except FileNotFoundError:
                bills_df = pd.DataFrame(columns=["Month", "Category", "Amount", "Description", "Type", "Service Number"])

            # Generate bill data based on the connection type
            if connection_type == "Household":
                generated_data = generate_household_bill_data(service_number)
                flagh=1
            elif connection_type == "Business":
                generated_data = generate_business_bill_data(service_number)
                flagb=1

            # Append and save the generated data to the bills DataFrame
            bills_df = pd.concat([bills_df, pd.DataFrame(generated_data)], ignore_index=True)
            bills_df.to_excel(EXCEL_BILLS, index=False)

            # Output the generated data
            st.write("Generated Bill Data:")
            st.write(pd.DataFrame(generated_data))
        else:
            st.warning("Please enter a valid service number.")

# ---- GRAPHICAL REPORTS SECTION ----
elif page == "Graphical Reports":
    st.title("Graphical Reports - Monthly Bills")
    try:
        bills_df = pd.read_excel(EXCEL_BILLS)
        if bills_df.empty:
            st.warning("No data available. Please enter bill data first.")
        else:
            st.subheader("All Bills Data")
            bills_df = bills_df.sort_values(by="Month", ascending=True)
            st.write(bills_df)

            bills_df["Month_Name"] = bills_df["Month"].apply(lambda x: date(1900, x, 1).strftime('%B'))
            household_data = bills_df[bills_df["Type"] == "Household"]
            business_data = bills_df[bills_df["Type"] == "Business"]

            monthly_household_totals = household_data.groupby("Month_Name")["Amount"].sum().reset_index()
            monthly_business_totals = business_data.groupby("Month_Name")["Amount"].sum().reset_index()

            monthly_household_totals["Month_Name"] = pd.to_datetime(monthly_household_totals["Month_Name"], format='%B').dt.month
            monthly_business_totals["Month_Name"] = pd.to_datetime(monthly_business_totals["Month_Name"], format='%B').dt.month

            monthly_household_totals = monthly_household_totals.sort_values(by="Month_Name")
            monthly_business_totals = monthly_business_totals.sort_values(by="Month_Name")

            monthly_household_totals["Month_Name"] = monthly_household_totals["Month_Name"].apply(lambda x: date(1900, x, 1).strftime('%B'))
            monthly_business_totals["Month_Name"] = monthly_business_totals["Month_Name"].apply(lambda x: date(1900, x, 1).strftime('%B'))

            st.subheader("Monthly Total Bills - Household")
            st.table(monthly_household_totals)
            st.subheader("Monthly Total Bills - Business")
            st.table(monthly_business_totals)

            st.subheader("Monthly Bills Overview - Household")
            st.bar_chart(monthly_household_totals.set_index("Month_Name")["Amount"])
            st.subheader("Monthly Bills Overview - Business")
            st.bar_chart(monthly_business_totals.set_index("Month_Name")["Amount"])

    except Exception as e:
        st.error(f"Error loading reports: {e}")

# ---- APPLIANCE VOLTAGE MONITORING SECTION ----
elif page == "Appliance Voltage Monitoring":
    st.title("Appliance Voltage Monitoring with Email Alerts")
    
    # Form for Appliance Entry
    with st.form("appliance_form"):
        st.subheader("Enter Appliance Details")
        item = st.text_input("Appliance Name (e.g., Fan, AC, TV):", placeholder="Enter appliance name")
        kilovolts = st.number_input("Kilovolts (kV):", min_value=0.0, step=0.1)
        start_time = st.time_input("Start Time")
        max_limit = st.number_input("Daily Voltage Limit (kV):", min_value=0.0, step=0.1)
        email = st.text_input("Email for Alerts", placeholder="Enter email for voltage alerts")

        submitted = st.form_submit_button("Save Appliance Data")
        if submitted and item and email:
            new_data = {
                "Item": item,
                "Kilovolts (kV)": kilovolts,
                "Start Time": start_time.strftime("%H:%M"),
                "Max Limit (kV)": max_limit,
                "Total Volts": 0,
                "Email": email
            }
            appliance_data_df = pd.concat([appliance_data_df, pd.DataFrame([new_data])], ignore_index=True)
            appliance_data_df.to_excel(EXCEL_APPLIANCE_DATA, index=False)
            st.success(f"Appliance data for '{item}' saved successfully!")

    # Automatic Monitoring Loop
    st.subheader("Monitoring Appliances...")
    progress_bar = st.progress(0)

    for i in range(5):  # Number of auto-refresh cycles
        for index, row in appliance_data_df.iterrows():
            item = row["Item"]
            kilovolts = row["Kilovolts (kV)"]
            start_time_str = row["Start Time"]
            max_limit = row["Max Limit (kV)"]
            email = row["Email"]

            # Calculate total hours since the start time
            today = datetime.today()
            start_time = datetime.strptime(start_time_str, "%H:%M")
            start_datetime = datetime.combine(today, start_time.time())
            current_time = datetime.now()
            total_hours = max((current_time - start_datetime).total_seconds() / 3600, 0)  # Ensure non-negative
            total_volts = round(kilovolts * total_hours, 2)

            # Send email if the limit is exceeded
            if total_volts > max_limit:
                subject = f"⚠Voltage Limit Exceeded for {item}⚠"
                body = f"Warning! {item} exceeded its daily voltage limit.\nTotal Volts: {total_volts} kV\nLimit: {max_limit} kV\nPlease Turn Off Your {item}"
                send_email(subject, body, email)
                st.warning(f"Alert: {item} exceeded its limit! Email sent to {email}.")

            # Update Total Volts
            appliance_data_df.at[index, "Total Volts"] = total_volts
            appliance_data_df.to_excel(EXCEL_APPLIANCE_DATA, index=False)

        progress_bar.progress((i + 1) / 5)
        time.sleep(1800)  # Pause 10 seconds before the next refresh cycle
        st.rerun()  # Auto-refresh Streamlit app

# ---- ELECTRICITY BILL PREDICTION SECTION ----
elif page == "Electricity Bill Prediction":
    st.title("Electricity Bill Prediction")

    try:
        # Load data
        bills_df = pd.read_excel(EXCEL_BILLS)
        electricity_data = bills_df[bills_df['Category'] == 'Electricity']

        if electricity_data.empty:
            st.warning("No electricity bill data available. Please enter data first.")
        else:
            # Prepare the features (X) and target (y)
            X = electricity_data[['Month']].values  # Month as the independent variable
            y = electricity_data['Amount'].values  # Amount as the dependent variable

            # Train a linear regression model
            model = LinearRegression()
            model.fit(X, y)

            # Predict the amount for the next month
            next_month = np.array([[electricity_data['Month'].max() + 1]])
            predicted_amount = model.predict(next_month)

            # Check if there's business data
            if "Business" in electricity_data['Type'].values:
                flagb = 1
            else:
                flagb = 0

            # Check if there's household data
            if "Household" in electricity_data['Type'].values:
                flagh = 1
            else:
                flagh = 0

            # Separate predictions for Household and Business
            if(flagb == 1):
                business_data = electricity_data[electricity_data["Type"] == "Business"]
                X_business = business_data[['Month']].values
                y_business = business_data['Amount'].values
                model_business = LinearRegression()
                model_business.fit(X_business, y_business)
                predicted_business = model_business.predict(np.array([[business_data['Month'].max() + 1]]))
                units_business = predicted_business[0] / 2  # ₹2 per unit
                st.write(f"Predicted Electricity Bill for Business for Month {next_month[0][0]} is expected to be: ₹{abs(int(predicted_business[0]))}")
                st.write(f"Units Consumed by Business for Month {next_month[0][0]} is expected to be: {abs(round(units_business, 2))} units")

            if(flagh == 1):
                household_data = electricity_data[electricity_data["Type"] == "Household"]
                X_household = household_data[['Month']].values
                y_household = household_data['Amount'].values
                model_household = LinearRegression()
                model_household.fit(X_household, y_household)
                predicted_household = model_household.predict(np.array([[household_data['Month'].max() + 1]]))
                units_household = predicted_household[0] / 1.5  # ₹1.5 per unit
                st.write(f"Predicted Electricity Bill for Household for Month {next_month[0][0]} is expected to be: ₹{abs(int(predicted_household[0]))}")
                st.write(f"Units Consumed by Household for Month {next_month[0][0]} is expected to be: {abs(round(units_household, 2))} units")

    except Exception as e:
        st.write("Error Occurred!!!")
        st.write(str(e))  # Print the error to understand what went wrong

elif st.button("Clear Data"):
    clear_data()
