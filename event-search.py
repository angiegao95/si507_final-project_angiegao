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

def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)

def make_request_using_cache_crawl(endurl):
    baseurl = 'https://www.fairsandfestivals.net/states/'

    if endurl in EVENT_DICTION:
        print("Fetching cached data...")
        return EVENT_DICTION[endurl]

    else:
        print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(baseurl+endurl)
        EVENT_DICTION[endurl] = resp.text
        dumped_json_cache = json.dumps(EVENT_DICTION)
        fw = open(CACHE_EVENT,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return EVENT_DICTION[endurl]

def make_request_using_cache_json(CACHE_DICTION, CACHE_FNAME, baseurl, params):
    unique_ident = params_unique_combination(baseurl,params)

    if unique_ident in CACHE_DICTION:
        # print("Fetching cached data...")
        return CACHE_DICTION[unique_ident]

    else:
        # print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(baseurl, params=params)
        CACHE_DICTION[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

## Generate Event Database
def init_event_db(db_name):
    DB_FNAME = db_name
    try:
        conn = sqlite.connect(DB_FNAME)
    except Error as e:
        print(e)

    cur = conn.cursor()

    statement = '''
        DROP TABLE IF EXISTS 'Events';
    '''
    cur.execute(statement)

    statement = '''
        DROP TABLE IF EXISTS 'EventType';
    '''
    cur.execute(statement)

    statement = '''
        DROP TABLE IF EXISTS 'Types';
    '''
    cur.execute(statement)
    conn.commit()

    create_events_table = '''
        CREATE TABLE 'Events' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT NOT NULL,
            'Date' TEXT NOT NULL,
            'City' TEXT NOT NULL,
            'State' TEXT NOT NULL,
            'Address' TEXT NOT NULL,
            'Description' TEXT NOT NULL
        )
    '''
    cur.execute(create_events_table)

    create_types_table = '''
        CREATE TABLE 'Types' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'TypeName' TEXT NOT NULL
        )
    '''
    cur.execute(create_types_table)

    create_eventtype_table = '''
        CREATE TABLE 'EventType' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'EventId' INTEGER NOT NULL,
            'TypeId' INTEGER NOT NULL
        )
    '''
    cur.execute(create_eventtype_table)
    conn.commit()

    all_event_types = ['Art', 'Food', 'Craft', 'Commercial', 'Music']
    for t in all_event_types:
        insert_statement = '''
            INSERT INTO Types
            VALUES (?, ?)
        '''
        params = (None,t)
        cur.execute(insert_statement, params)

    conn.commit()
    conn.close()

def populate_event_db():
    pass

## Define Search Related Functions
def search_events_by_state(state_abbr):
    #Crawl the events in the state
    event_text = make_request_using_cache_crawl(state_abbr)
    event_soup = BeautifulSoup(event_text, 'html.parser')
    event_rows = event_soup.find_all(class_='event')[:50]

    #Get the detail information of the event
    for event in event_rows:
        event_title = event.find('h4').text

        event_date_ls = event.find(class_='date').text.replace(',',' ').split()
        month_dict = {'January':'01', 'February':'02', 'March':'03', 'April':'04','May':'05', 'June':'06', 'July':'07', 'August':'08', 'September':'09',
            'October':'10', 'November':'11', 'December':'12'}
        event_date = '{}-{}-{}'.format(event_date_ls[2],month_dict[event_date_ls[0]],event_date_ls[1])

        event_city = event.find(class_='city').text
        event_state = event.find(class_='state').text

        event_address = ' '.join(event.find(class_='location').text.split())
        event_desc = event.find_all('tr')[1].find_all('td')[1].text[:-18].strip()
        event_type = []
        type_container = event.find(class_='vendors').find_all('li')
        for t in type_container:
            event_type.append(t.text)

        # Populate event data to DB
        global DB_FNAME
        conn = sqlite.connect(DB_FNAME)
        cur = conn.cursor()
        insert_statement = '''
            INSERT INTO Events
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        params = (None, event_title, event_date, event_city, event_state, event_address, event_desc)
        cur.execute(insert_statement, params)
        conn.commit()
        for t in  event_type:
            insert_statement = '''
                INSERT INTO EventType (EventId, TypeId)
                SELECT E.Id, T.Id
                FROM Events AS E, Types AS T
                WHERE E.Name = ?
                	AND T.TypeName = ?
            '''
            params = (event_title, t)
            cur.execute(insert_statement, params)

        conn.commit()
        conn.close()


DB_FNAME = 'event_db.sqlite'
# init_event_db(DB_FNAME)
search_events_by_state('MN')
