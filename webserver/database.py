from flask import Flask, request
from flask_cors import CORS
import redis
import json


app = Flask(__name__)
CORS(app)

# Connect to redis server
redis_server = redis.Redis("localhost", decode_responses=True, charset="unicode_escape")

@app.route('/drone', methods=['POST'])
def drone():

    # Extract drone information from the request JSON
    drone = request.get_json()
    droneID = drone['id']
    drone_longitude = drone['longitude']
    drone_latitude = drone['latitude']
    drone_status = drone['status']
    droneIP = request.remote_addr

    # Info dict to be stored
    drone_info = {
        'id': droneID,
        'longitude': drone_longitude,
        'latitude': drone_latitude,
        'status': drone_status,
        'ip': droneIP
    }

    # Convert drone_info dict to JSON string before storing
    drone_info_json = json.dumps(drone_info)

    # Store the JSON string in Redis hash with key as drone ID
    redis_server.hset("drones", droneID, drone_info_json)


    # =======================================================================================
    return 'Data recieved and stored successfully'

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5001')
