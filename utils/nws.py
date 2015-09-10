'''
NWS Data feed

Copywrite (c) 2015 Charles P Kollar

'''

import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

def build_request(lat, lon, begin_datetime, end_datetime, products):
    '''
    Build a request for the time period and products requested for the NWS.
    
    :param lat: The latitude for the point
    :type decimal number

    :param lon: The longitude for the point
    :type decimal number

    :param begin_datetime: The beginning time for the forecast.
    :type datetime

    :param end_datetime: The ending time for the forecast.
    :type datetime

    :param products: An vector of product strings to request.
    :type vector of strings

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
    '''
    Build a request for the time period of a day and products requested for the NWS.
    
    :param lat: The latitude for the point
    :type decimal number

    :param lon: The longitude for the point
    :type decimal number

    :param begin_datetime: The beginning time for the forecast.
    :type datetime

    :param products: An vector of product strings to request.
    :type vector of strings

    :return: request url
    :rtype: string
    '''
    end_datetime = begin_datetime + timedelta(days=1)
    return build_request(lat, lon, begin_datetime, end_datetime, products)

def get_day_time_temp_dewpt(lat, lon):
    '''
    Forcast for a 24 hr peroid at a given point on the map <lat, lon>,
    
    :param lat: The latitude for the point
    :type decimal number
    
    :param lon: The longitude for the point
    :type decimal number

    :return: An array of dictionaries that contain the readings.
    :rtype: array
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
        readings = []
        # Create a list of dictionary readings...
        for i in range(len(time)):
            reading = { 'time' : time[i], 'temp' : temp[i], 'dewpt' : dewpt[i], }
            readings.append(reading)
        return readings
    # The user clicked sowhere on the map where the NWS returns no data...
    # It also looks like some places in Canada and Mexico return NULL for data
    # This we do not handle, but just let it showup in the UI...
    return []
