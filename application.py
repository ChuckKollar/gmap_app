'''
This is the Flask backend for the server that will display a map for the user and
and empty table. Javascript in the HTML will geolocate the map so that it is centered
on the user's location. When the user clicks on the map, a handler executes a Ajax call
POST that comes to the server (here) with the <lat,lng> of the location that the user
clicked on. The server contatcs the National Weather Service (NWS) Data feed
http://graphical.weather.gov/xml/rest.php
and retrieves a one day forecest for that <lat,lng> which (currently) consists of the
Temperature, and Dew Poing. This is then sent back to the frontend via json where
the front end uses the data to replace the table in the DOM of the web page.

http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html
Using application.py as the filename and providing a callable application object
(the Flask object, in this case) allows AWS Elastic Beanstalk to easily find your
application's code.

Deployed at...
http://gwmap-env-ze2z8wipcu.elasticbeanstalk.com/

Copywrite (c) 2015 Charles P Kollar

'''
from flask import Flask, send_file, request, json, jsonify, send_from_directory
import os

from utils import nws, geo

'''
http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html

Using application.py as the filename and providing a callable application object
(the Flask object, in this case) allows AWS Elastic Beanstalk to easily find your
application's code.

Flask will look for templates in the /templates folder
'''
application = Flask(__name__, static_url_path='')


@application.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # This will put up a map that is geolocated to the user...
        return send_file('templates/gmap.html')
    
    # This should be a POST method with the moused lat and lng...
    lat = request.json['lat']
    lng = request.json['lng']
    countrycode = geo.get_countrycode(lat, lng)
    readings = []
    if countrycode == 'US':
        # XML REST api to get the 24-hr forecast for this lat/lng
        # from the National Weather Service...
        time, temp, dewpt = nws.get_day_time_temp_dewpt(lat, lng)
        # Create a list of dictionary readings...
        for i in range(len(time)):
            reading = { 'time':time[i], 'temp':temp[i], 'dewpt':dewpt[i] }
            readings.append(reading)
    #import ipdb; ipdb.set_trace()
    # return the data to the front end...
    json_ret = jsonify(countrycode=countrycode, readings=readings)
    return json_ret


# http://stackoverflow.com/questions/20646822/how-to-serve-static-files-in-flask
@application.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


@application.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)


# http://flask.pocoo.org/docs/0.10/patterns/favicon/
# http://www.freefavicon.com/freefavicons/objects/iconinfo/map-pin-152-195874.html
@application.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(application.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


if __name__ == "__main__":
    # Setting debug to True enables debug output, and reload on code changes.
    # This line should be removed before deploying a production app.
    application.debug = True
    # http://flask.pocoo.org/docs/0.10/quickstart/
    # Externally Visible Server
    # This tells your operating system to listen on all public IPs.
    application.run(host='0.0.0.0')
