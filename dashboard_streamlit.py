# Import necessary libraries and modules
import psutil  # Library for system monitoring
import time  # Library for handling time-related operations
from threading import Thread  # Multi-threading support
import GPUtil  # GPU monitoring library
import streamlit as st  # Web app creation library
import pandas as pd  # Data manipulation library
import warnings  # Library for warning handling
import altair as alt  # Declarative statistical visualization library
import matplotlib.pyplot as plt  # Plotting library

# Suppress import warnings
warnings.filterwarnings("ignore")

# Define a function to create a usage chart
def create_usage_chart(cpu_data: list, memory_data: list, gpu_data: list) -> plt:
    # Create a chart with the latest data
    plt.figure(figsize=(10, 6))

    # Set the background color to black
    plt.gca().set_facecolor('black')

    # Plot CPU Usage
    plt.plot(cpu_data, label='CPU Usage (%)', color='green')

    # Plot Memory Usage
    plt.plot(memory_data, label='Memory Usage (%)', color='blue')

    # Plot GPU Usage
    plt.plot(gpu_data, label='GPU Usage (%)', color='orange')

    # Set y-axis range between 0 and 100
    plt.ylim(0, 100)

    # Set labels and title
    plt.xlabel('Time')
    plt.ylabel('Percentage')
    plt.title('CPU, Memory, and GPU Usage')

    # Get the legend frame and set face color for the legend
    legend = plt.legend()
    legend.get_frame().set_facecolor('black')

    # Get the legend texts and set color
    for text in legend.get_texts():
        text.set_color('white')

    # Set the background color of the entire plot
    plt.gca().set_facecolor('black')

    return plt

# Define a function to check system conditions
def check_system_conditions() -> dict:
    # Get CPU usage for each core
    cpu_percent = psutil.cpu_percent()
    cpu_percent_per_core = psutil.cpu_percent(percpu=True)
    used_cores = sum(1 for percent in cpu_percent_per_core if percent > 0)

    # Get memory information
    memory_info = psutil.virtual_memory()
    memory_used_gb = memory_info.used / (1024 ** 3)  # Convert bytes to GB
    memory_percent = memory_info.percent

    # Get GPU information
    gpu_info = GPUtil.getGPUs()[0]
    gpu_percent = gpu_info.load * 100  # GPU usage in percentage
    gpu_memory_used_gb = (gpu_info.memoryTotal * (gpu_percent / 100)) / 1000  # GPU memory used in GB

    # Collect data in a dictionary
    result: dict = {
        'CPU Usage (%)': cpu_percent,
        'Used Cores': used_cores,
        'Memory Usage (GB)': memory_used_gb,
        'Memory Usage (%)': memory_percent,
        'GPU Usage (GB)': float(gpu_memory_used_gb),
        'GPU Usage (%)': gpu_percent
    }

    # Print the information
    print(f"System Conditions:\n"
          f"  CPU Usage (%): {result['CPU Usage (%)']} |"
          f"  Used Cores: {result['Used Cores']} |"
          f"  Memory Usage (GB): {result['Memory Usage (GB)']:.2f} GB |"
          f"  Memory Usage (%): {result['Memory Usage (%)']}% |"
          f"  GPU Usage (GB): {result['GPU Usage (GB)']:.2f} GB |"
          f"  GPU Usage (%): {result['GPU Usage (%)']}%")

    return result

# Streamlit app
st.title("Real-time System Monitor")
st.write("Updated every 2 seconds")

# Initial placeholder dictionaries for each variable
cpu_usage_dict: dict = {'CPU Usage (%)': 0}
used_cores_dict: dict = {'Used Cores': 0}
memory_usage_gb_dict: dict = {'Memory Usage (GB)': 0}
memory_usage_percent_dict: dict = {'Memory Usage (%)': 0}
gpu_usage_gb_dict: dict = {'GPU Usage (GB)': 0}
gpu_usage_percent_dict: dict = {'GPU Usage (%)': 0}

# Create empty elements for each variable
cpu_usage_element = st.empty()
used_cores_element = st.empty()
memory_usage_gb_element = st.empty()
memory_usage_percent_element = st.empty()
gpu_usage_gb_element = st.empty()
gpu_usage_percent_element = st.empty()

chart_element = st.empty()

# Lists to store historical data for chart plotting
memory_usage_gb_data: list = []
gpu_usage_gb_data: list = []
cpu_usage_data: list = []

# Infinite loop to continuously update and display system conditions
while True:
    # Get system conditions
    current_conditions = check_system_conditions()

    # Update the dictionaries with new values
    cpu_usage_dict['CPU Usage (%)'] = current_conditions['CPU Usage (%)']
    used_cores_dict['Used Cores'] = current_conditions['Used Cores']
    memory_usage_gb_dict['Memory Usage (GB)'] = current_conditions['Memory Usage (GB)']
    memory_usage_percent_dict['Memory Usage (%)'] = current_conditions['Memory Usage (%)']
    gpu_usage_gb_dict['GPU Usage (GB)'] = current_conditions['GPU Usage (GB)']
    gpu_usage_percent_dict['GPU Usage (%)'] = current_conditions['GPU Usage (%)']

    # Display the updated system conditions within the same div for each variable
    cpu_usage_element.write(f"CPU Usage (%): {cpu_usage_dict['CPU Usage (%)']}")
    used_cores_element.write(f"Used Cores: {used_cores_dict['Used Cores']}")
    memory_usage_gb_element.write(f"Memory Usage (GB): {memory_usage_gb_dict['Memory Usage (GB)']:.2f} GB")
    memory_usage_percent_element.write(f"Memory Usage (%): {memory_usage_percent_dict['Memory Usage (%)']}%")
    gpu_usage_gb_element.write(f"GPU Usage (GB): {gpu_usage_gb_dict['GPU Usage (GB)']:.2f} GB")
    gpu_usage_percent_element.write(f"GPU Usage (%): {gpu_usage_percent_dict['GPU Usage (%)']}%")

    # Update the chart with the latest data
    memory_usage_gb_data.append(memory_usage_percent_dict['Memory Usage (%)'])
    gpu_usage_gb_data.append(gpu_usage_percent_dict['GPU Usage (%)'])
    cpu_usage_data.append(cpu_usage_dict['CPU Usage (%)'])

    memory_usage_gb_data = memory_usage_gb_data[-100:]
    gpu_usage_gb_data = gpu_usage_gb_data[-100:]
    cpu_usage_data = cpu_usage_data[-100:]

    chart_data = pd.DataFrame({
        'Memory Usage %': memory_usage_gb_data,
        'GPU Usage %': gpu_usage_gb_data,
        'CPU Usage %': cpu_usage_data
    })

    cpu_usage_data.append(current_conditions['CPU Usage (%)'])
    memory_usage_gb_data.append(current_conditions['Memory Usage (%)'])
    gpu_usage_gb_data.append(current_conditions['GPU Usage (%)'])

    # Keep only the last 100 data points
    cpu_usage_data = cpu_usage_data[-100:]
    memory_usage_gb_data = memory_usage_gb_data[-100:]
    gpu_usage_gb_data = gpu_usage_gb_data[-100:]

    # Create the chart
    chart = create_usage_chart(cpu_usage_data, memory_usage_gb_data, gpu_usage_gb_data)

    # Display the chart with fixed y-axis range
    chart_element.pyplot(chart)

    # Add a short sleep to prevent excessive updates
    time.sleep(2)
