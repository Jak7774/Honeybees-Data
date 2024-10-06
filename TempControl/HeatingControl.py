import threading
from gpiozero import DigitalOutputDevice
from gpiozero import Device
from time import sleep
import time
from SerialHandler import ArduinoSerialHandler

class HeatingControl:
    def __init__(self, relay_pin, serial_handler):
        self.relay = DigitalOutputDevice(relay_pin)
        self.serial_handler = serial_handler
        self.heating_thread = None
        self.heating_enabled = False
        self.stop_request = threading.Event()
        self.start_time = time.time()

    def turn_on(self):
        self.relay.on()

    def turn_off(self):
        self.relay.off()
    
    def is_heating(self):
        return self.relay.is_active

    def cycle(self, duration_on, duration_off, cycles):
        for _ in range(cycles):
            self.turn_on()
            sleep(duration_on)
            self.turn_off()
            sleep(duration_off)
            if self.stop_request.is_set():
                break

    def start_heating(self, temp_outside):
        self.heating_enabled = True
        self.stop_request.clear()
        #self.heating_thread = threading.Thread(target=self._heating_thread)
        self.heating_thread = threading.Thread(target=self._heating_thread, args=(temp_outside,))
        self.heating_thread.start()

    def stop_heating(self):
        self.heating_enabled = False
        self.stop_request.set()
        if self.heating_thread:
            self.heating_thread.join()
                
    def _heating_thread(self, temp_outside):
        while self.heating_enabled and not self.stop_request.is_set():
            if temp_outside < 0:
                print("Super Cold! Starting Cold Heating Cycle")
                self.cold_weather_cycle()
            if temp_outside >= 0:
                print("Standard Heating Cycle")
                self.standard_cycle()

    def cold_weather_cycle(self):
        self.cycle(duration_on=300, duration_off=30, cycles=3)
        self.cycle(duration_on=180, duration_off=30, cycles=5)  # Adjust cycles as needed
        self.cycle(duration_on=90, duration_off=30, cycles=10)

    def standard_cycle(self):
        self.cycle(duration_on=120, duration_off=30, cycles=5)
        self.cycle(duration_on=60, duration_off=30, cycles=5)  # Adjust cycles as needed
        self.cycle(duration_on=30, duration_off=30, cycles=10)

def read_temperatures(serial_handler):
    serial_handler.open_connection()
    temp_brood, temp_outside = serial_handler.read_temperatures()
    serial_handler.close_connection()
    return temp_brood, temp_outside

def main():
    # Create Instance of Arduino Serial Handler
    arduino_serial = ArduinoSerialHandler(port='/dev/ttyACM0', baud_rate=9600)

    # Set up heating control
    relay_pin = 14  # Replace with the actual GPIO pin for your relay switch
    heating_control = HeatingControl(relay_pin, arduino_serial)
    
    timeout = 1500 # 25 Minutes
    running = True
    try:
        while running:
            if heating_control.is_heating():
                status = "High"
            else:
                status = "Low"
            # Read temperature from the Arduino
            temp_brood, temp_outside = read_temperatures(arduino_serial)
            #temp_outside = 8
            print(f"Brood temperature: {temp_brood}°C, ", f"Outside temperature: {temp_outside}°C,", f"Pin Status: {status}")
            heating_control.temp_outside = temp_outside
            
            if temp_brood < 20 and temp_brood > -50 and not heating_control.heating_enabled:
                # Activate heating function
                print("Activating heating...")
                heating_control.start_heating(temp_outside)

            elif temp_brood > 20 and heating_control.heating_enabled:
                # Turn off heating function
                print("Brood temperature above 15°C. Turning off heating.")
                heating_control.stop_heating()
            
            arduino_serial.close_connection()
            
            elapsed_time = time.time() - heating_control.start_time
            if elapsed_time >= timeout: # 1200 = 5 Minutes
                print("Script has met time limit, exiting.")
                running = False
                heating_control.stop_heating() 
                #break
            
            sleep(30)  # Adjust the sleep duration as needed
        
    except KeyboardInterrupt:
        print("Program terminated by user.")
        heating_control.stop_heating()
        arduino_serial.close_connection()
        running = False
        
    finally:
         arduino_serial.close_connection()
         if heating_control.heating_enabled:
             heating_control.stop_heating()
             
running = False
         
if __name__ == "__main__":
    main()
