'''
Geocoding Service

http://www.geonames.org/export/

'''

import requests


def build_request(request_type, lat, lng, username):
    '''
    Build a request for the time period and products requested for the NWS.
    
    :param lat: The latitude for the point
    :type decimal number

    :param lng: The longitude for the point
    :type decimal number

    :param username: The username on geonames.org to use in making the request.
    :type string

    :return: request url
    :rtype: string
    '''
    url = 'http://api.geonames.org/'+\
      request_type+'?'+\
      'lat='+str(lat)+\
      '&lng='+str(lng)+\
      '&username='+username
    return url

def get_countrycode(lat, lng):
    '''
    Get the country code (two letter; upper case) for the <lat,lng> provided.
    
    :param lat: The latitude for the point
    :type decimal number
    
    :param lng: The longitude for the point
    :type decimal number

    :return: A two character string of the country code.
    :rtype: string
    '''
    url = build_request('countrycode', lat, lng, 'cpk412')
    code_str = requests.get(url).content
    return code_str.strip()
