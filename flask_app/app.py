from flask import Flask, render_template
import RPi.GPIO as GPIO
from smbus2 import SMBus # For I2C
import time



app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Route to send alerts
@app.route('/alert', methods=['POST'])
def alert():
    return 'alert placeholder'

    
if __name__ == '__main__':
    app.run(debug=True, host='')
