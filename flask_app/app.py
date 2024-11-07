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





# #Ambient Light Sensor
# #--------------------------------
# import smbus2
# import time

# # Define the I2C bus (Raspberry Pi uses bus 1 for I2C)
# bus = smbus2.SMBus(1)

# # Define the I2C address of the light sensor (adjust based on actual address, e.g., 0x10)
# SENSOR_ADDRESS = 0x4a  # Replace with the actual address if different

# # Set up the GPIO for servo motor
# SERVO_PIN = 17  # Change to the GPIO pin you've connected the servo to
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(SERVO_PIN, GPIO.OUT)
# servo = GPIO.PWM(SERVO_PIN, 50)  # 50Hz frequency for servo

# # Lux threshold to trigger servo movement
# THRESHOLD_HIGH = 25000

# # Function to control the servo motor
# def control_servo(turn_open):
#     if turn_open:
#         servo.ChangeDutyCycle(10)  # Full speed clockwise (2.0ms pulse)
#     else:
#         servo.ChangeDutyCycle(5)  # Full speed counter-clockwise (1.0ms pulse)

# # Function to read light level from the sensor
# def read_light_level():
#     """
#     Reads light level from the 0-200klx ambient light sensor.
#     Assumes the sensor returns a 2-byte lux value directly.
#     """
#     try:
#         # Read 2 bytes from the sensor
#         data = bus.read_i2c_block_data(SENSOR_ADDRESS, 0x00, 2)
        
#         # Convert the data to a lux value
#         lux = (data[0] << 8) | data[1]
#         return lux
#     except Exception as e:
#         print(f"Error reading light level: {e}")
#         return None

# def main():
#     print("Ambient Light Sensor Test - Raw Light Level (Lux)")
#     servo.start(0)  # Initialize servo without movement
#     try:
#         while True:
#             # Read the light level
#             lux = read_light_level()
            
#             if lux is not None:
#                 print(f"Light Level: {lux} lux")
                
#                 # Check light level and control the servo based on threshold
#                 if lux >= THRESHOLD_HIGH:
#                     control_servo(turn_open=True)  # Open servo when outside threshold
#                     print("Lux is above threshold, rotating counter-clockwise")
#                 else:
#                     control_servo(turn_open=False)  # Close servo when within threshold
#                     print("Lux is below threshold, rotating clockwise")

#             else:
#                 print("Error: Unable to read sensor.")
                
#             time.sleep(1)  # Delay for 1 second

# # Let the parent set threshold values for the light sensor
# # If the light level is above the threshold, the servo will turn on

#     except KeyboardInterrupt:
#         print("Program interrupted. Exiting...")

#     finally:
#         servo.ChangeDutyCycle(7.5)  # Stop servo (set it to neutral position)
#         servo.stop()
#         GPIO.cleanup()  # Clean up GPIO on exit



# Grove Sound Sensor
#--------------------------------

import spidev
import time

# Set up SPI communication
spi = spidev.SpiDev()
spi.open(0, 0)  # Open bus 0, device 0 (CE0)
spi.max_speed_hz = 1350000  # Set the SPI clock speed

# Function to read data from MCP3008
def read_channel(channel):
    try:
        # Send start bit, single-ended bit, and channel bits
        adc = spi.xfer2([1, (8 + channel) << 4, 0])
        # Process returned bits to get the 10-bit ADC value
        data = ((adc[1] & 3) << 8) + adc[2]
        return data
    except IOError as e:
        print("SPI Communication Error:", e)
        return None  # Return None if there's an error in reading data

try:
    while True:
        # Read sound level from channel 0 (where SIG is connected)
        sound_level = read_channel(0)
        
        # Check if sound_level is None (error in reading)
        if sound_level is not None:
            print("Sound Level:", sound_level)
        else:
            print("Failed to read sound level. Retrying...")
        
        time.sleep(1)  # Adjust the delay as needed

except KeyboardInterrupt:
    print("Program stopped by user")

except Exception as e:
    print("An unexpected error occurred:", e)

finally:
    spi.close()



if __name__ == '__main__':
    main()

    #try:
        # app.run(host='192.168.152.59', port=5000)
    #main()
    # finally:
    #     GPIO.cleanup()  # Clean up GPIO on exit