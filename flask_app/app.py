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
SENSOR_ADDRESS = 0x4a  # Replace with the actual address if different

# Set up the GPIO for servo motor
SERVO_PIN = 17  # Change to the GPIO pin you've connected the servo to
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50)  # 50Hz frequency for servo

# Lux threshold to trigger servo movement
THRESHOLD_HIGH = 25000

# Function to control the servo motor
def control_servo(turn_open):
    if turn_open:
        servo.start(7.5)  # Adjust pulse width as needed to turn
    else:
        servo.start(2.5)  # Adjust pulse width as needed to turn back
    time.sleep(1)  # Delay for servo to move
    servo.stop()

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
    servo.start(0)  # Initialize servo without movement
    try:
        while True:
            # Read the light level
            lux = read_light_level()
            
            if lux is not None:
                print(f"Light Level: {lux} lux")
                
                # Check light level and control the servo based on threshold
                if lux >= THRESHOLD_HIGH:
                    control_servo(turn_open=True)  # Open servo when outside threshold
                    time.sleep(1)  # Delay for 1 second
                else:
                    control_servo(turn_open=False)  # Close servo when within threshold
                    time.sleep(1)  # Delay for 1 second
            else:
                print("Error: Unable to read sensor.")
                
            time.sleep(1)  # Delay for 1 second

# Let the parent set threshold values for the light sensor
# If the light level is above the threshold, the servo will turn on

    except KeyboardInterrupt:
        print("Program interrupted. Exiting...")

if __name__ == '__main__':
    main()

    
    
    
    
    #try:
        # app.run(host='192.168.152.59', port=5000)
    #main()
    # finally:
    #     GPIO.cleanup()  # Clean up GPIO on exit