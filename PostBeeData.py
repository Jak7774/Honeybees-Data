#!/usr/bin/env python
import requests
import serial
import time
import json
from datetime import datetime

# Define the USB port for the Arduino
usb_port = '/dev/ttyACM0'

# Initialize serial connection
try:
    arduino = serial.Serial(usb_port, 9600, timeout=5)  # Added timeout to prevent hanging
    arduino.flush()
except serial.SerialException as e:
    print(f"Error opening serial port {usb_port}: {e}")
    exit()

# Function to validate sensor data
def validate_sensor_data(sensor_json):
    """Check if all required keys exist and their values are within expected ranges."""
    required_keys = {"temp1", "temp2", "temp3", "temp4", "humid1", "humid2", "weight"}

    # Ensure all required keys are present
    if not required_keys.issubset(sensor_json.keys()):
        print("Error: Missing keys in sensor data.")
        return False

    try:
        # Extract and validate values
        if not (-40 <= sensor_json["temp1"] <= 120 and
                -40 <= sensor_json["temp2"] <= 120 and
                -40 <= sensor_json["temp3"] <= 120 and
                -40 <= sensor_json["temp4"] <= 120):
            print("Error: Temperature values out of range.")
            return False

        if not (0 <= sensor_json["humid1"] <= 100 and 0 <= sensor_json["humid2"] <= 100):
            print("Error: Humidity values out of range.")
            return False

        if not (sensor_json["weight"] > 1000):
            print("Error: Weight value too low.")
            return False

    except (ValueError, TypeError):
        print("Error: Invalid data type detected.")
        return False

    return True  # Data is valid

# Function to read and parse JSON sensor data
def get_sensor_data(max_retries=3):
    """Reads sensor data from Arduino and validates it before returning."""
    for attempt in range(max_retries):
        try:
            arduino.write(b'P')  # Request data from Arduino
            time.sleep(0.5)  # Allow time for Arduino to respond
            sensor_data = arduino.readline().decode('utf-8').strip()  # Read response

            # Debugging: Print received data
            print(f"Attempt {attempt + 1}: Raw data received:", sensor_data)

            # Attempt to parse JSON
            sensor_json = json.loads(sensor_data)

            # Validate data
            if validate_sensor_data(sensor_json):
                return sensor_json  # Return the valid sensor data

            print("Invalid data received. Retrying...")

        except json.JSONDecodeError:
            print("Error: Received invalid JSON. Retrying...")
        except Exception as e:
            print(f"Error reading from Arduino: {e}")
        
        time.sleep(1)  # Wait before retrying

    print("Max retries reached. No valid sensor data obtained.")
    return None  # Return None if no valid data is retrieved

# Get valid sensor data
sensor_data = get_sensor_data()

if sensor_data:
    # Get the current timestamp
    dt = datetime.now()
    sensor_data['timestamp'] = dt.strftime("%d/%m/%YT%H:%M:%S")

    print("Data to be sent:", sensor_data)

    # Define the URL of the web server
    url = 'https://beeserver-94cf5d3aff73.herokuapp.com/post_endpoint'

    # Send data to the server
    try:
        response = requests.post(url, json=sensor_data)  # Send as JSON
        if response.status_code == 200:
            print("Data sent successfully!")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print("An error occurred while sending data:", e)
else:
    print("No valid data to send. Exiting.")
