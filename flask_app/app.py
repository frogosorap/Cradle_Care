from flask import Flask, render_template
#import RPi.GPIO as GPIO
#from smbus2 import SMBus # For I2C
import time



app = Flask(__name__)

#Home page
@app.route('/')
def index():
    return render_template('index.html')

#Cradle Care explanation page
@app.route('/explanation')
def explanation():
    return render_template('explanation.html')

#Cradle Care learn more page
@app.route('/learnmore')
def learnmore():
    return render_template('learnmore.html')

#Google Login page - Will be implemented later
@app.route('/login')
def login():
    return render_template('login.html') 




# Route to send alerts
@app.route('/alert', methods=['POST'])
def alert():
    return 'alert placeholder'

    
if __name__ == '__main__':
#   try:
        app.run(host='0.0.0.0', port=5000)
#    finally:
#        GPIO.cleanup()  # Clean up GPIO on exit


