from flask import Flask, render_template,session, abort, redirect, request
# import RPi.GPIO as GPIO
# from smbus2 import SMBus # For I2C
import time


import requests
import pathlib
import os
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")

# app.secret_key = "cradle_care_jrmy_secret_key_7923"


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID_LOGIN")
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secrets.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes = ["https://www.googleapis.com/auth/userinfo.profile","https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri = "http://127.0.0.1:5000/callback"
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
@login_is_required
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
                
                # Check light level and control the servo based on threshold
                if lux >= THRESHOLD_HIGH:
                    control_servo(turn_open=True)  # Open servo when outside threshold
                    print("Lux is above threshold, rotating clockwise")
                else:
                    control_servo(turn_open=False)  # Close servo when within threshold
                    print("Lux is below threshold, rotating counter-clockwise")

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

if __name__ == '__main__':
    main()

    
    
    
    
    #try:
        # app.run(host='192.168.152.59', port=5000)
    #main()
    # finally:
    #     GPIO.cleanup()  # Clean up GPIO on exit