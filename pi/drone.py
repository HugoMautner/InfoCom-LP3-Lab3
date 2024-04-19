from flask import Flask, request
from flask_cors import CORS
import subprocess
import  requests
from simulator import idle
from sense_hat import SenseHat
sense = SenseHat()
sense.clear()
sense.low_light = True


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'


# temp id
myID = "DRONE_1"

# Initial coords (set to 0 for now)
current_longitude = 13.233290
current_latitude = 55.715810


# Set up dict of the drone's info, ip is added on server side
drone_info = {  
    'id': myID,
    'longitude': current_longitude,
    'latitude': current_latitude,
    'status': 'idle'
}

# IP of the server, port to database
SERVER = "http://192.168.0.1:5001/drone"
with requests.Session() as session:
    resp = session.post(SERVER, json=drone_info)
    sense.clear()
    sense.set_pixels(idle)


# Function to read the last coordinates from the text file
def read_last_coordinates():
    with open("last_coordinates.txt", "r") as file:
        last_coords = file.read().split(',')
        return float(last_coords[0]), float(last_coords[1])

@app.route('/', methods=['POST'])
def main():

    coords = request.json

    # Get the last coordinates from the text file
    current_longitude = coords['current'][0]
    current_latitude = coords['current'][1]

    # They are now our current position to be passed to the simulator
    # current_longitude = last_longitude
    # current_latitude = last_latitude

    # Start the simulator subprocess
    from_coord = coords['from']
    to_coord = coords['to']
    subprocess.Popen(["python3", "simulator.py", '--clong', str(current_longitude), '--clat', str(current_latitude),
                                                 '--flong', str(from_coord[0]), '--flat', str(from_coord[1]),
                                                 '--tlong', str(to_coord[0]), '--tlat', str(to_coord[1]),
                                                 '--id', myID
                    ])
    return 'New route received'

if __name__ == '__main__':
    app.run(debug=True, host='192.168.0.2')
