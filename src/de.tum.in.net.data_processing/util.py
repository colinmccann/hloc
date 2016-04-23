#!/usr/bin/env python3
"""Some utility functions"""
from __future__ import print_function
from math import radians, cos, sin, asin, sqrt
from subprocess import check_output
from string import printable

ACCEPTED_CHARACTER = '{0},.-_'.format(printable[0:62])

def gps_distance_haversine(location1, location2):
    """
    Calculate the distance (km) between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1 = radians(float(location1['lon']))
    lat1 = radians(float(location1['lat']))
    lon2 = radians(float(location2['lon']))
    lat2 = radians(float(location2['lat']))
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    tmp = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    ftmp = 2 * asin(sqrt(tmp))
    # Radius of earth in kilometers. Use 3956 for miles
    return ftmp * 6371


def is_in_radius(location1, location2, radius):
    """
    Calculate the distance (km) between two points
    using the equirectangular distance approximation
    """
    lon1 = radians(float(location1['lon']))
    lat1 = radians(float(location1['lat']))
    lon2 = radians(float(location2['lon']))
    lat2 = radians(float(location2['lat']))
    # Radius of earth in kilometers. Use 3956 for miles
    return (radius / 6371)**2 >= (((lon2 - lon1) * cos(0.5*(lat2+lat1)))**2 + (lat2 - lat1)**2)


def location_encoding_func(obj):
    """Overrides the default method from the JSONEncoder"""
    if isinstance(obj, Location) or isinstance(obj, Domain):
        return {'__class__': 'Location'}.update(obj.dict_representation())

    raise TypeError('Object not handled by the JSON encoding function')


def count_lines(filename):
    """"Opens the file at filename than counts and returns the number of lines"""
    count = check_output(['wc', '-l', filename])
    lineCount = int(str(count, encoding='utf-8').split(' ')[0])

    print('Linecount for file: {0}'.format(lineCount))
    return lineCount


def get_path_filename(path):
    """Extracts the filename from a path string"""
    if path[-1] == '/':
        raise NameError('The path leads to a directory')
    fileIndex = path.find('/')
    filename = path[:]

    while fileIndex >= 0:
        filename = filename[fileIndex + 1:]
        fileIndex = filename.find('/')

    return filename


class GPSLocation(object):
    """holds the coordinates"""
    lat = None
    lon = None

    def __init__(self, lat, lon):
        """init"""
        self.lat = lat
        self.lon = lon

    def is_near(self, location, radius):
        """Returns a True if the location is within the radius"""
        lon1 = radians(float(self.lon))
        lat1 = radians(float(self.lat))
        lon2 = radians(float(location.lon))
        lat2 = radians(float(location.lat))
        # Radius of earth in kilometers. Use 3956 for miles
        return (radius / 6371)**2 >= (((lon2 - lon1) * cos(0.5*(lat2+lat1)))**2 + (lat2 - lat1)**2)


class Location(GPSLocation):
    """
    A location object with the location name, coordinates and location codes
    Additionally information like the population can be saved
    """

    def __init__(self, lat, lon, city_name=None, state=None, state_code=None, population=0):
        """init"""
        self.id = None
        self.city_name = city_name
        self.state = state
        self.state_code = state_code
        self.population = population
        self.airport_info = None
        self.locode = None
        self.clli = []
        self.alternate_names = []
        super().__init__(lat, lon)

    def add_airport_info(self):
        """Creates and sets a new empty AirportInfo object"""
        if self.airport_info is None:
            self.airport_info = AirportInfo()

    def add_locode_info(self):
        """Creates and sets a new empty """
        if self.locode is None:
            self.locode = LocodeInfo()

    def dict_representation(self):
        """Returns a dictionary with the information of the object"""
        airport_dict = None
        if self.airport_info:
            airport_dict = self.airport_info.dict_representation()

        locode_dict = None
        if self.locode:
            locode_dict = self.locode.dict_representation()

        return {
            'city_name': self.city_name,
            'state': self.state,
            'state_code': self.state_code,
            'population': self.population,
            'airport_info': airport_dict,
            'locode': locode_dict,
            'clli': self.clli,
            'alternate_names': self.alternate_names
        }


class AirportInfo(object):
    """Holds a list of the differen airport codes"""

    def __init__(self):
        """init"""
        self.iata_codes = []
        self.icao_codes = []
        self.faa_codes = []

    def dict_representation(self):
        """Returns a dictionary with the information of the object"""
        return {
            'iata_codes': self.iata_codes,
            'icao_codes': self.icao_codes,
            'faa_codes': self.faa_codes
        }


class LocodeInfo(object):
    """Holds a list of locode codes"""

    def __init__(self):
        """init"""
        self.place_codes = []
        self.subdivision_codes = []

    def dict_representation(self):
        """Returns a dictionary with the information of the object"""
        return {
            'place_codes': self.place_codes,
            'subdivision_codes': self.subdivision_codes
        }

class Domain(object):
    """Holds the information for one domain"""

    def __init__(self, domain_name, ip_address=None, ipv6_address=None):
        """init"""
        self.domain_name = domain_name
        self.ip_address = ip_address
        self.ipv6_address = ipv6_address

    def dict_representation(self):
        """Returns a dictionary with the information of the object"""
        return {
            'domain_name': self.domain_name,
            'ip_address': self.ip_address,
            'ipv6_address': self.ipv6_address
        }
