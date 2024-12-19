import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.linear_model import LinearRegression

# Function to simulate and analyze energy consumption
def analyze_energy_consumption(working_hours, sleeping_hours, num_people, items, home_type):
    # Parse working and sleeping hours from user input
    working_start, working_end = map(int, working_hours.split('-'))
    sleeping_start, sleeping_end = map(int, sleeping_hours.split('-'))

    # Define average energy consumption for common appliances (in kWh per day)
    appliance_energy = {
        'Fridge': 1.5,     # kWh/day
        'TV': 0.2,         # kWh/day
        'Air Conditioner': 2.0,  # kWh/day
        'Washing Machine': 0.5,  # kWh/day
        'Microwave': 0.6,  # kWh/day
        'Heater': 3.0,     # kWh/day
        'Fan': 0.4,        # kWh/day
    }

    # Define home type multipliers for energy consumption adjustment
    home_type_multipliers = {
        'Building': 1.5,
        'Apartment': 1.2,
        'Hut': 0.8,
        'Villa': 1.3,
        'Condo': 1.1
    }

    # Adjust the energy consumption multiplier based on the home type
    home_multiplier = home_type_multipliers.get(home_type, 1.0)  # Default to 1 if invalid home type

    # Calculate total energy consumption for the household
    total_energy_consumption = 0
    for item in items:
        total_energy_consumption += appliance_energy.get(item, 0) * num_people  # Multiplied by number of people
    
    # Adjust the total energy consumption based on the home type
    total_energy_consumption *= home_multiplier

    # Simulate energy consumption data for a 24-hour period (in kWh)
    hours = np.arange(0, 24)
    energy_consumption = np.random.normal(loc=total_energy_consumption/24, scale=0.2, size=24)  # Average consumption over 24 hours

    # Optional: Add a few known peaks
    energy_consumption[working_start] = total_energy_consumption / 12  # Peak at start of work hours
    energy_consumption[working_end] = total_energy_consumption / 10  # Peak at end of work hours
    energy_consumption[sleeping_start] = total_energy_consumption / 24  # Lower consumption during sleeping hours
    energy_consumption[sleeping_end] = total_energy_consumption / 24  # Lower consumption during sleeping hours

    # Find peak consumption periods
    peak_threshold = np.percentile(energy_consumption, 90)  # Set threshold at the 90th percentile
    peak_hours = hours[energy_consumption > peak_threshold]
    peak_consumption = energy_consumption[energy_consumption > peak_threshold]

    # Return the data for plotting and peak information
    return hours, energy_consumption, peak_hours, peak_consumption, peak_threshold, working_start, working_end, sleeping_start, sleeping_end

# Function to predict electricity bill for next month
def predict_electricity_bill(current_month):
    # Simulate a simple linear regression model for predicting the electricity bill
    model = LinearRegression()
    X = np.array([range(1, 13)]).reshape(-1, 1)
    y = np.random.uniform(100, 500, 12)  # Simulated data for prediction

    model.fit(X, y)
    predicted_bill = model.predict(np.array([[current_month + 1]]))[0]
    return round(predicted_bill, 2)

# Streamlit UI with Tiled Layout
st.title('Energy Consumption and Bill Prediction Tracker')

# Sidebar Navigation
page = st.sidebar.radio("Select a page", ["Energy Consumption Tracker", "Electricity Bill Prediction"])

# Energy Consumption Tracker
if page == "Energy Consumption Tracker":
    # Create columns for the inputs
    col1, col2 = st.columns(2)

    # Input fields for number of people and items (placed in the first column)
    with col1:
        num_people = st.number_input("Enter the number of people living in the house:", min_value=1, max_value=10, value=1)
        home_type = st.selectbox(
            "Select the type of home:",
            options=['Building', 'Apartment', 'Hut', 'Villa', 'Condo']
        )

    # Input fields for appliances and hours (placed in the second column)
    with col2:
        items = st.multiselect(
            "Select the appliances/items in your home:",
            options=['Fridge', 'TV', 'Air Conditioner', 'Washing Machine', 'Microwave', 'Heater', 'Fan'],
            default=['Fridge', 'TV']
        )
        working_hours = st.text_input("Enter your working hours (e.g., 9-17 for 9 AM to 5 PM):", "9-17")
        sleeping_hours = st.text_input("Enter your sleeping hours (e.g., 22-6 for 10 PM to 6 AM):", "22-6")

    # Run the analysis when the button is clicked
    if st.button('Analyze Energy Consumption'):
        hours, energy_consumption, peak_hours, peak_consumption, peak_threshold, working_start, working_end, sleeping_start, sleeping_end = analyze_energy_consumption(working_hours, sleeping_hours, num_people, items, home_type)
        
        # Display all consumption times
        st.subheader("Energy Consumption Throughout the Day:")
        for hour, consumption in zip(hours, energy_consumption):
            st.write(f"At {hour}:00, consumption was {consumption:.2f} kWh")

        # Display peak consumption periods
        st.subheader("Peak Consumption Periods (above the 90th percentile):")
        for hour, consumption in zip(peak_hours, peak_consumption):
            st.write(f"At {hour}:00, consumption was {consumption:.2f} kWh")

        # Plot the energy consumption data
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(hours, energy_consumption, label='Energy Consumption (kWh)', color='b', marker='o')
        ax.axhline(y=peak_threshold, color='r', linestyle='--', label="90th Percentile Threshold")
        
        # Highlight working and sleeping hours
        ax.fill_between(np.arange(working_start, working_end), 0, energy_consumption[working_start:working_end], color='yellow', alpha=0.3, label="Working Hours")
        ax.fill_between(np.arange(sleeping_start, sleeping_end), 0, energy_consumption[sleeping_start:sleeping_end], color='purple', alpha=0.3, label="Sleeping Hours")
        
        # Customize plot
        ax.set_title("Energy Consumption Throughout the Day")
        ax.set_xlabel("Hour of Day")
        ax.set_ylabel("Energy Consumption (kWh)")
        ax.set_xticks(hours)
        ax.grid(True)
        ax.legend()

        # Display the plot
        st.pyplot(fig)

# Electricity Bill Prediction
elif page == "Electricity Bill Prediction":
    st.title("Electricity Bill Prediction for the Next Month")

    # Get user input for the next month prediction
    current_month = datetime.now().month
    predicted_units = st.number_input(f"Enter units consumed in month {current_month + 1}:", min_value=0)
    
    if predicted_units:
        predicted_bill = predict_electricity_bill(current_month)

        st.write(f"Predicted bill for the next month: ₹{predicted_bill}")
