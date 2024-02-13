from os import fdopen
from flask import Flask, render_template, request
from flask.json import jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import time
import redis
import pickle
import json

app = Flask(__name__)
CORS(app)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'

# Connect to redis server
redis_server = redis.Redis("localhost", decode_responses=True, charset="unicode_escape")

# Translate OSM coordinate (longitude, latitude) to SVG coordinates (x,y).
# Input coords_osm is a tuple (longitude, latitude).
def translate(coords_osm):
    x_osm_lim = (13.143390664, 13.257501336)
    y_osm_lim = (55.678138854000004, 55.734680845999996)

    x_svg_lim = (212.155699, 968.644301)
    y_svg_lim = (103.68, 768.96)

    x_osm = coords_osm[0]
    y_osm = coords_osm[1]

    x_ratio = (x_svg_lim[1] - x_svg_lim[0]) / (x_osm_lim[1] - x_osm_lim[0])
    y_ratio = (y_svg_lim[1] - y_svg_lim[0]) / (y_osm_lim[1] - y_osm_lim[0])
    x_svg = x_ratio * (x_osm - x_osm_lim[0]) + x_svg_lim[0]
    y_svg = y_ratio * (y_osm_lim[1] - y_osm) + y_svg_lim[0]

    return x_svg, y_svg

@app.route('/', methods=['GET'])
def map():
    return render_template('index.html')

@app.route('/get_drones', methods=['GET'])
def get_drones():
    
    #connect to redis server and retrieve drone information
    drone_info_from_redis = redis_server.hgetall("drones")
    
    #create empty dict
    drone_dict = {}
    
    #Iterate through the drone information obtained from redis
    for drone_id, drone_info in drone_info_from_redis.items():

        # Decode the pickled data
        decoded_info = pickle.loads(drone_info.encode())

        #retrieve the latitutde, longitude and status
        latitude = decoded_info['latitude']
        longitude = decoded_info['longitude']
        status = decoded_info['status']
        
        
        #translate to svg
        svg_longitude, svg_latitude = translate((float(longitude), float(latitude)))
        
        #update dict
        drone_dict[drone_id] = {'longitude': svg_longitude, 'latitude': svg_latitude, 'status': status}
        
    
    return jsonify(drone_dict)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5000')
