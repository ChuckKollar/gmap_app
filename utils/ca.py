'''
Canadian weather service XML:

http://dd.weather.gc.ca/citypage_weather/docs/README_citypage_weather.txt

Copywrite (c) 2015 Charles P Kollar

'''

import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import csv
import numpy as np

'''
First read the file...
site_list_en_url = 'http://dd.weather.gc.ca/citypage_weather/docs/site_list_en.csv'

Which gives the following information
<*code, town, *province, *lat, *lng>

Which can be used in this URL to get the forecast after we determine
the closest *lat, *lng from the input lat, lng...
http://dd.weather.gc.ca/citypage_weather/xml/<<province>>/<<code>>_e.xml

The forecast information looks like this...
<forecast>
 <period textForecastName=Monday">Monday</period>
 <temperatures>
  <temperature unitType="metric" units="C" class="high/low">9</temperature>
  <relativeHumidity units="%">55</relativeHumidity>
 </temperatures>
</forecast>
'''

# http://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons-in-python
class Sites(object):
    '''
    This is a singleton that returns the sites available in Canada.
    '''
    _instance = None
    sites = []

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Sites, cls).__new__(cls, *args, **kwargs)
        return cls._instance
                                 
    def __init__(self):
        Sites.sites = self.fetch_sites()

    def fetch_sites(self):
        sites_list = []
        site_list_en_url = 'http://dd.weather.gc.ca/citypage_weather/docs/site_list_en.csv'
        csv_str = requests.get(site_list_en_url).content
        site_csv = csv.reader(csv_str.split('\n'), delimiter=',')
        # ['Site Names', '', '', '', '']
        site_csv.next()
        # ['Codes', 'English Names', 'Province Codes', 'Latitude', 'Longitude']
        site_csv.next()
        # Need to skip the first two lines which contain the header...
        for row in site_csv:
            if not row:
                break
            code = row[0]
            town = row[1]
            province_code = row[2]
            try:
                lat = float(row[3][:-1])
                lng = float(row[4][:-1])
            except ValueError:
                continue
            if row[3].endswith('S'):
                lat = -lat
            if row[4].endswith('W'):
                lng = - lng
            site = { 'code' : code,
                     'town' : town,
                     'province_code' : province_code,
                     'lat' : lat,
                     'lng' : lng,
                     'loc' : (lat, lng),
                      }
            sites_list.append(site)
        return sites_list

    def get(self):
        return Sites.sites

# http://codereview.stackexchange.com/questions/28207/finding-the-closest-point-to-a-list-of-points
def distance(pt_1, pt_2):
    pt_1 = np.array((pt_1[0], pt_1[1]))
    pt_2 = np.array((pt_2[0], pt_2[1]))
    return np.linalg.norm(pt_1-pt_2)

def closest_loc(loc, locs):
    pt = []
    dist = 9999999
    for l in locs:
        if distance(loc, l) <= dist:
            dist = distance(loc, l)
            pt = l
    return pt
            
def build_request(lat, lon):
    '''
    Build a request for the location in Canadia
    
    :param lat: The latitude for the point
    :type decimal number

    :param lon: The longitude for the point
    :type decimal number

    :return: request url
    :rtype: string
    '''

    # Need to find the closest <lat,lng> to that in the sites list...
    sites = Sites().get()
    locs = [ site['loc'] for site in sites ]
    # Find the closest location to the site...
    loc = closest_loc((lat, lon), locs)
    # Lookup the site by the location...
    site = (site for site in sites if site['loc'] == loc).next()
    # Create the URL to retrieve the XML...
    url = 'http://dd.weather.gc.ca/citypage_weather/xml/'+site['province_code']+'/'+site['code']+'_e.xml'
    return url

def get_forecast(lat, lon):
    '''
    Forcast for a 24 hr peroid at a given point on the map <lat, lon>,
    
    :param lat: The latitude for the point
    :type decimal number
    
    :param lon: The longitude for the point
    :type decimal number

    :return: An array of dictionaries that contain the readings.
    :rtype: array
    '''
    url = build_request(lat, lon)
    xml_str = requests.get(url).content
    # https://docs.python.org/2/library/xml.etree.elementtree.html
    root = ET.fromstring(xml_str)
    forecast_group = root.find('forecastGroup')
    # return an array of dictionaries containing the forecasts for the period...
    if forecast_group is not None:
        readings = []
        for child in forecast_group:
            if child.tag == 'forecast':
                period = child.find('period')
                temps = child.find('temperatures')
                temp = temps.find('temperature')
                temp_units = temp.attrib['units']
                temp_text = temp.text + temp_units
                reading = { 'period' : period.text, 'temp' : temp_text }
                readings.append(reading)
        return readings
    # The user clicked sowhere on the map where the NWS returns no data...
    # It also looks like some places in Canada and Mexico return NULL for data
    # This we do not handle, but just let it showup in the UI...
    return []

if __name__ == "__main__":
    forecast = get_forecast(54.72, -113.28)
    #import ipdb; ipdb.set_trace()
    print forecast
