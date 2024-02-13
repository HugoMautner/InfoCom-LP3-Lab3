from cmath import pi
from flask import Flask, request, render_template, jsonify
from flask.globals import current_app 
from geopy.geocoders import Nominatim
from flask_cors import CORS
import redis
import json
import requests

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'

# Connect to your redis server
redis_server = redis.Redis(host="localhost", port="6379", decode_responses=True, charset="unicode_escape")

geolocator = Nominatim(user_agent="my_request")
region = ", Lund, Skåne, Sweden"

# Example to send coords as request to the drone
def send_request(drone_url, coords):
    with requests.Session() as session:
        resp = session.post(drone_url, json=coords)

@app.route('/planner', methods=['POST'])
def route_planner():

    # Decode geolocations from request
    Addresses =  json.loads(request.data.decode())
    FromAddress = Addresses['faddr']
    ToAddress = Addresses['taddr']
    from_location = geolocator.geocode(FromAddress + region, timeout=None)
    to_location = geolocator.geocode(ToAddress + region, timeout=None)

    if from_location is None:
        message = 'Departure address not found, please input a correct address'
        return message
    elif to_location is None:
        message = 'Destination address not found, please input a correct address'
        return message
    else:
        # If the coodinates are found by Nominatim, the coords will need to be sent the a drone that is available
        coords = {'from': (from_location.longitude, from_location.latitude),
                  'to': (to_location.longitude, to_location.latitude),
                  }
        
        # Find an available drone in the database
        available_drone = None
        for drone_id in redis_server.hkeys("drones"):
            status = redis_server.hget("drones", drone_id)['status']
            if status == 'idle':
                available_drone = drone_id
                break
        
        if available_drone is None:
            message = 'No available drone, try later'
        else:
            # Get the IP address of the available drone
            drone_info = redis_server.hget("drones", available_drone)
            drone_ip = json.loads(drone_info)['ip']
            DRONE_URL = 'http://' + drone_ip + ':5000'

            # Send coordinates to the URL of available drone
            send_request(DRONE_URL, coords)
            message = 'Got address and sent request to the drone'

    return message


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5002')
