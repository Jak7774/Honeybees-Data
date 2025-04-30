#!/usr/bin/env python
import requests
import time
import json
import random
from datetime import datetime
import argparse

def generate_fake_data():
    return {
        "temp1": round(random.uniform(15, 35), 2),  # Brood
        "temp2": round(random.uniform(10, 30), 2),  # Super
        "temp3": round(random.uniform(5, 25), 2),   # Outside
        "temp4": round(random.uniform(0, 20), 2),   # Roof
        "humid1": round(random.uniform(30, 80), 2), # Outside humidity
        "humid2": round(random.uniform(30, 80), 2), # Roof humidity
        "weight": round(random.uniform(1500, 5000), 2)  # Weight in grams
    }

sensor_data = generate_fake_data()


if sensor_data:
    # Get the current timestamp
    dt = datetime.now()
    sensor_data['timestamp'] = dt.strftime("%d/%m/%YT%H:%M:%S")

    # Add BeeHive ID - Current set here but eventually set from config file
    sensor_data['beehive_id'] = 2

    print("Data to be sent:", sensor_data)

    # Define the URL of the web server
    url = 'http://localhost:5000/post_endpoint'  # Debug Version
    #url = 'https://beeserver-94cf5d3aff73.herokuapp.com/post_endpoint'

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