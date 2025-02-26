#!/usr/bin/env python
import serial
import time
import csv
import json
from datetime import datetime

usb_port = '/dev/ttyACM0'
arduino = serial.Serial(usb_port, 9600)
time.sleep(2)
arduino.flush()

# Function to read data and ensure it has exactly 7 values
def get_sensor_data():
    while True:
        try:
            arduino.write(b'P')  # Request data from Arduino
            time.sleep(0.5)  # Allow time for Arduino to respond
            sensor_data = arduino.readline().decode('utf-8').strip()  # Read response

            # Debugging: Print received data
            print("Raw data received:", sensor_data)

            # Attempt to parse JSON
            sensor_json = json.loads(sensor_data)

            # Convert dictionary values to a list
            #sensor_values = list(sensor_json.values())
            sensor_values = ",".join(map(str, sensor_json.values()))


            return sensor_values  # Return the extracted values as a list

        except json.JSONDecodeError:
            print("Error: Received invalid JSON. Retrying...")
            time.sleep(1)
        except Exception as e:
            print(f"Error reading from Arduino: {e}")
            exit()

# Get valid sensor data
data = get_sensor_data()

dt = datetime.now()
str_dt = dt.strftime("%m/%d/%YT%H:%M:%S")

res = []
res.append(str_dt)
res.append(data)

print(res)

with open('/home/pi/Data.csv','a') as fd:
    writer = csv.writer(fd)
    writer.writerow(res)

