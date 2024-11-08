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




#Cradle Care explanation page
@app.route('/explanation')
def explanation():
    return render_template('explanation.html')

#Cradle Care learn more page
@app.route('/learnmore')
def learnmore():
    return render_template('learnmore.html')

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

    
if __name__ == '__main__':
    # try:
        app.run(host='0.0.0.0', port=5000, debug="on")
    # finally:
        # GPIO.cleanup()  # Clean up GPIO on exit


