'''
To Run these tests:

$ pip install nose
$ pip install ipdb
$ pip install httpretty
$ nosetests

'''
from unittest import TestCase
import httpretty

from datetime import datetime
import dateutil.parser

import utils.nws as nws

class NWSTestCase(TestCase):
    '''
    These are the test cases for the NWS utility.
    '''
    
    def test_build_request_a(self):

        begin_str = '2015-02-01T00:00:00'
        end_str   = '2015-02-02T00:00:00'
        begin_datetime  = dateutil.parser.parse(begin_str)
        end_datetime    = dateutil.parser.parse(end_str)

        url = nws.build_request(1.0, 2.0, begin_datetime, end_datetime, ['a', 'b', 'c'])

        url_test = 'http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdXMLclient.php?'+\
            'lat=1.0&lon=2.0&product=time-series&begin='+begin_str+'&end='+end_str+'&a=a&b=b&c=c'
            
        assert url == url_test
    
    def test_build_request_b(self):

        begin_str = '2015-02-01T00:00:00'
        end_str   = '2016-09-01T00:00:00'
        begin_datetime  = dateutil.parser.parse(begin_str)
        end_datetime    = dateutil.parser.parse(end_str)

        url = nws.build_request(11.0, -12.0, begin_datetime, end_datetime, ['one', 'two',])

        url_test = 'http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdXMLclient.php?'+\
            'lat=11.0&lon=-12.0&product=time-series&begin='+begin_str+'&end='+end_str+'&one=one&two=two'
            
        assert url == url_test
        
    
    def test_build_request_day(self):

        begin_str = '2015-02-01T00:00:00'
        end_str   = '2015-02-02T00:00:00'
        begin_datetime  = dateutil.parser.parse(begin_str)

        url = nws.build_request_day(11.0, -12.0, begin_datetime, ['one', 'two',])

        url_test = 'http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdXMLclient.php?'+\
            'lat=11.0&lon=-12.0&product=time-series&begin='+begin_str+'&end='+end_str+'&one=one&two=two'
            
        assert url == url_test
    '''        
    def test_get_day_time_temp_dewpt(self):
        time, temp, dewpt = nws.get_day_time_temp_dewpt(, lng)
        import ipdb; ipdb.set_trace()
    '''

