# SerialHandler.py
import serial
import time
import json  # Import JSON module

class ArduinoSerialHandler:
    def __init__(self, port, baud_rate):
        self.port = port
        self.baud_rate = baud_rate
        self.serial = None

    def open_connection(self):
        """Open serial connection."""
        self.serial = serial.Serial(self.port, self.baud_rate, timeout=5)  # Added timeout

    def close_connection(self):
        """Close serial connection."""
        if self.serial:
            self.serial.close()

    def read_temperatures(self, max_retries=3):
        """Read JSON data from Arduino and extract temperatures."""
        for _ in range(max_retries):
            try:
                self.serial.flush()
                self.serial.write(b'P')  # Request data from Arduino
                time.sleep(0.5)  # Allow time for Arduino to respond
                data = self.serial.readline().decode('utf-8').strip()  # Read response

                # Debugging: Print raw received data
                #print("Raw data received:", data)

                # Attempt to parse JSON
                sensor_json = json.loads(data)

                # Extract "temp1" and "temp3" values
                temp1 = float(sensor_json.get("temp1", 40))  # Default to 40 if missing
                temp3 = float(sensor_json.get("temp3", 30))  # Default to 30 if missing

                return temp1, temp3

            except json.JSONDecodeError:
                print("Error: Received invalid JSON. Retrying...")
                time.sleep(1)
            except ValueError:
                print("Error in Reading Values: Return defaults to safely stop heating")
                return 40, 30
            except serial.SerialException as e:
                print(f"Error reading temperatures: {e}")
                print("Retrying...")
                time.sleep(1)

        # If max retries are reached, return default values
        print("Max retries reached. Returning placeholder values.")
        return 40, 30  
