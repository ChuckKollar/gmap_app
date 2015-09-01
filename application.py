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

Copywrite (c) 2015 Charles P Kollar

'''
from flask import Flask, render_template, request, json, jsonify
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET

'''
http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html

Using application.py as the filename and providing a callable application object
(the Flask object, in this case) allows AWS Elastic Beanstalk to easily find your
application's code.
'''

# Flask will look for templates in the /templates folder
application = Flask(__name__)


'''
NWS Data feed
'''
def build_request(lat, lon, begin_datetime, end_datetime, products):
    '''
    Build a request for the time period and products requested.
    
    :param lat: latitude
    :type decimal number

    :return: request url
    :rtype: string
    '''
    # Get the iso8601 string representing the dates...
    begin_iso8601 = begin_datetime.isoformat()
    end_iso8601 = end_datetime.isoformat()
    url = 'http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdXMLclient.php?'+\
      'lat='+str(lat)+\
      '&lon='+str(lon)+\
      '&product=time-series&begin='+begin_iso8601+\
      '&end='+end_iso8601
    for prod in products:
        url += '&' +  prod + '=' + prod
    return url

def build_request_day(lat, lon, begin_datetime, products):
    end_datetime = begin_datetime + timedelta(days=1)
    return build_request(lat, lon, begin_datetime, end_datetime, products)

def get_day_time_temp_dewpt(lat, lon):
    '''
    For a 24 hr peroid at the given <lat, lon>,
    return three vectors for the: time, temp, and dew point forecast.
    '''
    url = build_request_day(lat, lon, datetime.now(), ['temp', 'dew'])
    xml_str = requests.get(url).content
    # https://docs.python.org/2/library/xml.etree.elementtree.html
    #import ipdb; ipdb.set_trace()
    root = ET.fromstring(xml_str)
    data = root.find('data')
    if data is not None:
        time_layout = data.find('time-layout')
        time = [svt.text for svt in time_layout.findall('start-valid-time')]
        parameters = data.find('parameters')
        temps = parameters.findall('temperature')
        temp = [t.text for t in temps[0].findall('value')]
        dewpt = [t.text for t in temps[1].findall('value')]
        return (time, temp, dewpt)
    # The user clicked sowhere on the map where the NWS returns no data...
    # It also looks like some places in Canada and Mexico return NULL for data
    # This we do not handle, but just let it showup in the UI...
    return ([], [], [])

@application.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # This will put up a map that is geolocated to the user...
        return render_template('gmap.html')
    
    # This should be a POST method with the moused lat and lng...
    lat = request.json['lat']
    lng = request.json['lng']
    # XML REST api to get the 24-hr forecast for this lat/lng...
    time, temp, dewpt = get_day_time_temp_dewpt(lat, lng)
    # return the data to the front end...
    json_ret = jsonify(time=time, temp=temp, dewpt=dewpt)
    return json_ret


if __name__ == "__main__":
    # Setting debug to True enables debug output, and reload on code changes.
    # This line should be removed before deploying a production app.
    application.debug = True
    # http://flask.pocoo.org/docs/0.10/quickstart/
    # Externally Visible Server
    # This tells your operating system to listen on all public IPs.
    application.run(host='0.0.0.0')
