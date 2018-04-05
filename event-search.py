import requests
import json
import plotly.plotly as py
from secrets import *
from bs4 import BeautifulSoup
import csv
import sqlite3 as sqlite
from sqlite3 import Error

class Event():
    def __init__(self, eventtype, name, date, desc):
        self.type = eventtype
        self.name = name
        self.date = date
        self.description = desc

        self.street = '123 Main St.'
        self.city = 'Smallville'
        self.state = 'KS'
        self.zip = '11111'
        self.lat = 0
        self.lng = 0

    def __str__(self):
        event_str = '[{}]{}({}): {}, {}, {}({})'.format(self.type, self.name, self.date, self.street, self.city, self.state, self.zip)
        return event_str

class Restaurant():
    def __init__(self, name):
        self.name = name

        self.street = '123 Main St.'
        self.city = 'Smallville'
        self.state = 'KS'
        self.zip = '11111'
        self.lat = 0
        self.lng = 0
    def __str__(self):
        rest_str = '{}: {}, {}, {}({})'.format(self.name, self.street, self.city, self.state, self.zip)
        return self.name

class ParkingStructure():
    def __init__(self, name):
        self.name = name

        self.street = '123 Main St.'
        self.city = 'Smallville'
        self.state = 'KS'
        self.zip = '11111'
        self.lat = 0
        self.lng = 0
    def __str__(self):
        rest_str = '{}: {}, {}, {}({})'.format(self.name, self.street, self.city, self.state, self.zip)
        return self.name

## Make Requests By Caching
CACHE_EVENT = 'event_data_cache_file.json'
CACHE_REST = 'restaurant_data_cache_file.json'
CACHE_PARKING = 'parking_data_cache_file.json'

try:
    cache_file = open(CACHE_EVENT, 'r')
    cache_contents = cache_file.read()
    EVENT_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    EVENT_DICTION = {}

try:
    cache_file = open(CACHE_REST, 'r')
    cache_contents = cache_file.read()
    REST_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    REST_DICTION = {}

try:
    cache_file = open(CACHE_PARKING, 'r')
    cache_contents = cache_file.read()
    PARKING_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    PARKING_DICTION = {}

## Generate Cache Database
DB_FNAME = 'event_db.sqlite'

try:
    conn = sqlite.connect(DB_FNAME)
except Error as e:
    print(e)


## Define Search Related Functions
def search_events():
    pass
