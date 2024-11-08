from flask import Flask, render_template,session, abort, redirect, request
import RPi.GPIO as GPIO
# from smbus2 import SMBus # For I2C
import json 
import time, threading
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory, PNOperationType

my_channel = "Cradle_Care_Channel"

import requests
import pathlib
import os
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from dotenv import load_dotenv


load_dotenv()
pnconfig = PNConfiguration()
pnconfig.subscribe_key = os.environ.get('PUBNUB_SUBSCRIBE_KEY')
pnconfig.publish_key = os.environ.get('PUBNUB_PUBLISH_KEY')
pnconfig.user_id = "cradle_care_user"
pubnub = PubNub(pnconfig)

def my_publish_callback(envelope, status):
    if not status.is_error():
        pass
    else:
        pass

class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):
        pass

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass
        elif status.category == PNStatusCategory.PNConnectedCategory:
            pubnub.publish().channel(my_channel).message('Connected to Pubnub').pn_async(my_publish_callback)
        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass

    def message(self, pubnub, message):
        print(message.message)


pubnub.add_listener(MySubscribeCallback())

def publish(channel, message):
    pubnub.publish().channel(channel).message(message).pn_async(my_publish_callback)


app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")
# app.secret_key = "cradle_care_jrmy_secret_key_7923"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID_LOGIN")
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secrets.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes = ["https://www.googleapis.com/auth/userinfo.profile","https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri = "http://192.168.152.59:5000/callback"
)

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)
        else:
            return function()
    return wrapper

#Landing page
@app.route('/')
def landingpage():
    return render_template('landingpage.html')

lux_readings = []  # Global list to store lux readings

@app.route('/light')
def light():
    lux = read_light_level()
    if lux is None:
        lux = "Error reading light level"
    return render_template('light.html', lux=lux)

# #Cradle Care explanation page
# @app.route('/explanation')
# def explanation():
#     return render_template('explanation.html')

# #Cradle Care learn more page
# @app.route('/learnmore')
# def learnmore():
#     return render_template('learnmore.html')

#Google Login page - Will be implemented later
@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session = cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    print(session["name"])
    return redirect("/index")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/index")
#@login_is_required
def index():
    # return f"Hello{session["google_id"]} <a href='/logout'><button>Logout</button></a>"
    return render_template('index.html')


# Route to send alerts
@app.route('/alert', methods=['POST'])
def alert():
    return 'alert placeholder'





#Ambient Light Sensor
#--------------------------------
import smbus2

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
        servo.ChangeDutyCycle(10)  # Full speed clockwise (2.0ms pulse)
    else:
        servo.ChangeDutyCycle(5)  # Full speed counter-clockwise (1.0ms pulse)

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
                lux_readings.append(lux)  # Append each reading to the list
                
                # Check light level and control the servo based on threshold
                if lux >= THRESHOLD_HIGH:
                    control_servo(turn_open=True)  # Open servo when outside threshold
                    print("Lux is above threshold, rotating clockwise")
                    publish(my_channel, {'light':'too bright'})
                else:
                    control_servo(turn_open=False)  # Close servo when within threshold
                    print("Lux is below threshold, rotating counter-clockwise")
                    publish(my_channel, {'light':'just right'})

            else:
                print("Error: Unable to read sensor.")
                
            time.sleep(1)  # Delay for 1 second

    

# Let the parent set threshold values for the light sensor
# If the light level is above the threshold, the servo will turn on

    except KeyboardInterrupt:
        print("Program interrupted. Exiting...")

    finally:
        servo.ChangeDutyCycle(7.5)  # Stop servo (set it to neutral position)
        servo.stop()
        GPIO.cleanup()  # Clean up GPIO on exit

# Grove Sound Sensor
#--------------------------------
import spidev
import time

# Set up SPI communication
spi = spidev.SpiDev()
spi.open(0, 1)  # Open bus 0, device 1 (CS1)
spi.max_speed_hz = 500000  # Lower SPI clock speed for stability (500 kHz)

# Function to read data from MCP3008
def read_channel(channel):
    try:
        # Send start bit, single-ended bit, and channel bits
        adc = spi.xfer2([1, (8 + channel) << 4, 0])

        # Debug print to show raw ADC response
        print("Raw ADC response:", adc)

        # Process returned bits to get the 10-bit ADC value
        data = ((adc[1] & 3) << 8) + adc[2]
        return data
    except IOError as e:
        print("SPI Communication Error:", e)
        return None  # Return None if there's an error in reading data

try:
    while True:
        # Test all channels (0 to 7) on the MCP3008
        for channel in range(8):
            level = read_channel(channel)
            print(f"Channel {channel} Level:", level)

            # Additional check: if level is 0, notify potential issue on that channel
            if level == 0:
                print(f"Warning: Channel {channel} reading is zero. Check sensor or wiring.")

        # Delay between each round of readings
        time.sleep(1)  # Adjust the delay as needed

except KeyboardInterrupt:
    print("SPI communication stopped")

finally:
    # Close the SPI connection properly
    spi.close()
    print("SPI interface closed.")





if __name__ == '__main__':
    main()
    sensorsThread = threading.Thread(target=read_light_level)
    sensorsThread.start()
    pubnub.subscribe().channels(my_channel).execute()
    app.run(host='0.0.0.0', port=5000)