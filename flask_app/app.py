# from flask import Flask, render_template
import RPi.GPIO as GPIO
from smbus2 import SMBus # For I2C
# import time



# app = Flask(__name__)

# #Home page
# @app.route('/')
# def index():
#     return render_template('index.html')

# #Cradle Care explanation page
# @app.route('/explanation')
# def explanation():
#     return render_template('explanation.html')

# #Cradle Care learn more page
# @app.route('/learnmore')
# def learnmore():
#     return render_template('learnmore.html')

# #Google Login page - Will be implemented later
# @app.route('/login')
# def login():
#     return render_template('login.html') 

# # Route to send alerts
# @app.route('/alert', methods=['POST'])
# def alert():
#     return 'alert placeholder'





#Ambient Light Sensor
#--------------------------------
import smbus2
import time

# Define the I2C bus (Raspberry Pi uses bus 1 for I2C)
bus = smbus2.SMBus(1)

# Define the I2C address of the light sensor (adjust based on actual address, e.g., 0x10)
SENSOR_ADDRESS = 0x10  # Replace with the actual address if different

# Function to read light level from the sensor
def read_light_level():
    """
    Reads light level from the 0-200klx ambient light sensor.
    Assumes the sensor returns a 2-byte lux value directly.
    """
    try:
        # Read 2 bytes from the sensor
        data = bus.read_i2c_block_data(SENSOR_ADDRESS, 0x00, 2)
        
        # Convert the data to a lux value
        lux = (data[0] << 8) | data[1]
        return lux
    except Exception as e:
        print(f"Error reading light level: {e}")
        return None

def main():
    print("Ambient Light Sensor Test - Raw Light Level (Lux)")
    
    try:
        while True:
            # Read the light level
            lux = read_light_level()
            
            if lux is not None:
                print(f"Light Level: {lux} lux")
            else:
                print("Error: Unable to read sensor.")
                
            time.sleep(1)  # Delay for 1 second
    
    except KeyboardInterrupt:
        print("Program interrupted. Exiting...")

if __name__ == '__main__':
    main()

    
    
    
    
    #try:
        # app.run(host='192.168.152.59', port=5000)
    #main()
    # finally:
    #     GPIO.cleanup()  # Clean up GPIO on exit