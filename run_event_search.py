import requests
import json
from secrets import *
from bs4 import BeautifulSoup
import csv
import sqlite3 as sqlite
from sqlite3 import Error
from event_plot import *
from event_db import *
from event_class import *

## Make Requests By Caching
CACHE_EVENT = 'event_data_cache_file.json'
CACHE_GOOGLEMAP = 'googlemap_data_cache_file.json'
CACHE_YELP = 'yelp_data_cache_file.json'

try:
    cache_file = open(CACHE_EVENT, 'r')
    cache_contents = cache_file.read()
    EVENT_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    EVENT_DICTION = {}

try:
    cache_file = open(CACHE_GOOGLEMAP, 'r')
    cache_contents = cache_file.read()
    MAP_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    MAP_DICTION = {}

try:
    cache_file = open(CACHE_YELP, 'r')
    cache_contents = cache_file.read()
    YELP_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    YELP_DICTION = {}

def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)

def make_request_using_cache_crawl(endurl):
    baseurl = 'https://www.fairsandfestivals.net/states/'

    if endurl in EVENT_DICTION:
        # print("Fetching cached data...")
        return EVENT_DICTION[endurl]

    else:
        # print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(baseurl+endurl)
        EVENT_DICTION[endurl] = resp.text
        dumped_json_cache = json.dumps(EVENT_DICTION)
        fw = open(CACHE_EVENT,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return EVENT_DICTION[endurl]

def make_request_using_cache_json(CACHE_DICTION, CACHE_FNAME, baseurl, params, headers=None):
    unique_ident = params_unique_combination(baseurl,params)

    if unique_ident in CACHE_DICTION:
        # print("Fetching cached data...")
        return CACHE_DICTION[unique_ident]

    else:
        # print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(baseurl, params=params, headers=headers)
        CACHE_DICTION[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]


## Define Search Related Functions
def search_place_location(address):
    search_keyword = address.replace(',','')
    baseurl = 'https://maps.googleapis.com/maps/api/place/textsearch/json?'
    params_text = {'query':search_keyword, 'key':google_places_key}
    place_json = make_request_using_cache_json(MAP_DICTION, CACHE_GOOGLEMAP, baseurl, params_text)

    try:
        result = place_json['results'][0]['geometry']['location']
    except:
        result = {'lat':0, 'lng':0}
    return result


def search_events_by_state(state_abbr):
    #Crawl the events in the state
    event_text = make_request_using_cache_crawl(state_abbr)
    event_soup = BeautifulSoup(event_text, 'html.parser')
    event_rows = event_soup.find_all(class_='event')[:100]

    #Get the detail information of the event
    for row in event_rows:
        event_title = row.find('h4').text

        event_date_ls = row.find(class_='date').text.replace(',',' ').split()
        month_dict = {'January':'01', 'February':'02', 'March':'03', 'April':'04','May':'05', 'June':'06', 'July':'07', 'August':'08', 'September':'09',
            'October':'10', 'November':'11', 'December':'12'}
        event_date = '{}-{}-{}'.format(event_date_ls[2],month_dict[event_date_ls[0]],event_date_ls[1])

        event_city = row.find(class_='city').text
        event_state = row.find(class_='state').text

        event_address = row.find(class_='location').text.split(',')[2].strip()
        event_desc = row.find_all('tr')[1].find_all('td')[1].text[:-18].strip()
        event_type = []
        type_container = row.find(class_='vendors').find_all('li')
        for t in type_container:
            event_type.append(t.text)
        event_location = search_place_location(event_address + ' '+ event_city + ' ' + event_state)

        insert_event_to_db(event_type, event_title, event_date, event_desc, event_address, event_city, event_state, event_location['lat'], event_location['lng'])


def search_nearby_restaurants(event):
    lat = event.lat
    lon = event.lon
    baseurl = 'https://api.yelp.com/v3/businesses/search'
    params = {'term':'food', 'latitude':lat, 'longitude':lon, 'limit':10, 'sort_by':'distance'}
    headers = {'Authorization': 'Bearer %s' % yelp_fusion_key}
    restaurant_json = make_request_using_cache_json(YELP_DICTION, CACHE_YELP, baseurl, params=params, headers=headers)
    nearby_restaurants = restaurant_json['businesses']

    restaurant_ls = []
    for r in nearby_restaurants:
        rating = r['rating']
        name = r['name']
        coordinate = r['coordinates']
        location = r['location']
        restaurant_ls.append(Restaurant(name,rating,coordinate['latitude'],coordinate['longitude'],location['address1'],location['city'],location['state']))

    return restaurant_ls

def search_nearby_parkings(event):
    lat = event.lat
    lon = event.lon
    baseurl = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
    params = {'location':'{},{}'.format(lat,lon),'type':'parking','rankby':'distance','limit':5,'key':google_places_key}
    parking_json = make_request_using_cache_json(MAP_DICTION, CACHE_GOOGLEMAP, baseurl, params=params)
    nearby_parkings = parking_json['results'][:5]

    parking_ls = []
    for p in nearby_parkings:
        name = p['name']
        location = p['geometry']['location']
        address = p['vicinity']
        parking_ls.append(ParkingStructure(name,address,location['lat'],location['lng']))

    return parking_ls

def run_event_search():
    list_events = []
    category_events = []

    print('Hi there! Welcome to this event search tool! (Enter "help" to browse commands supported)')
    command = input('Please enter your command: ')
    while command != 'exit':
        command_ls = command.replace('=',' ').split()
        if command_ls[0] == 'list':
            state_abbr = command_ls[1]
            if len(state_abbr) != 2:
                print('Invalid state abbreviation. Did you accidentally include any space in it?')
                command = input('Please re-enter your command: ')
            else:
                if not check_state_db(state_abbr):
                    search_events_by_state(state_abbr)

                if 'groupby'in command_ls:
                    g_comm = command_ls[command_ls.index('groupby') + 1]
                    map_type = 'state'
                    if g_comm == 'type':
                        list_events = group_event_by_type(state_abbr)
                        g_name = 'TypeName'
                        map_type = 'type'
                    elif g_comm == 'city':
                        list_events = group_event_by_city(state_abbr)
                        g_name = 'CityName'
                    else:
                        print('Invalid group command.')
                        command = input('Please re-enter your command: ')
                        continue
                else:
                        list_events = group_event_by_city(state_abbr)
                        g_name = 'CityName'
                        g_comm = 'city'
                        map_type = 'state'
                boundary = '*************** Event Overview ({}) ***************'.format(state_abbr)
                print(boundary)
                print('{:5}  {:25} {:5}'.format('Index',g_name,'EventCount'))
                i = 1
                type_name = []
                type_count = []
                for row in list_events:
                    type_name.append(row[0])
                    type_count.append(int(row[1]))
                    print('{:5}  {:25} {:5}'.format(i, row[0], row[1]))
                    i += 1

                print('*' * len(boundary))
                command = input('Please enter your command: ')

        elif command_ls[0] == 'more':
            if list_events != []:
                try:
                    result_i = int(command_ls[1]) - 1
                except:
                    result_i = -1

                if result_i != -1:
                    map_type = 'category'
                    category = list_events[result_i][0]
                    category_events = search_category_event(category, g_comm)
                    boundary = '*************  All Events ({}) *************'.format(category)
                    print(boundary)
                    i = 1
                    for e in category_events:
                        type_str = ''
                        for t in e.type:
                            type_str += t + ' '
                        print('{}. {}'.format(i, e.name))
                        print('   Date: {}'.format(e.date))
                        print('   Event Type: {}'.format(type_str))
                        print('   Address: {}'.format(e.address))
                        print('   Description: {}'.format(e.desc))
                        print('')
                        i += 1
                    print('*' * len(boundary))
                    command = input('Please enter your command: ')
                else:
                    command = input('Invalid index. Please re-enter your command: ')
            else:
                print('Please check the event overview by "list" command before go into details.')
                command = input('Please re-enter your command: ')

        elif command_ls[0] == 'nearby':
            if category_events != []:
                try:
                    event_i = int(command_ls[1]) - 1
                except:
                    event_i = -1

                if event_i != -1:
                    map_type = 'nearby'
                    target_event = category_events[event_i]
                    restaurant_ls = search_nearby_restaurants(target_event)
                    parking_ls = search_nearby_parkings(target_event)
                    boundary = '**********  {}: TOP 10 NEARBY RESTAURANTS **********'.format(target_event.name)
                    print(boundary)
                    i = 1
                    for r in restaurant_ls:
                        print('{}.'.format(i),r)
                        i += 1
                    print('*' * len(boundary))
                    print('')
                    i = 1
                    boundary = '*******  {}: TOP 5 NEAREST PARKING LOTS *******'.format(target_event.name)
                    print(boundary)
                    for p in parking_ls:
                        print('{}.'.format(i),p)
                        i += 1
                    print('*' * len(boundary))
                    command = input('Please enter your command: ')
                else:
                    command = input('Invalid index. Please re-enter your command: ')
            else:
                print('Please check the event category by "more" command before go into details.')
                command = input('Please re-enter your command: ')

        elif command == 'plot':
            if map_type == 'state':
                state_events = search_state_event(state_abbr)
                plot_state_map(state_events)
                print('*' * len(boundary))
                print('Generating visualization...')
                print('*' * len(boundary))
                command = input('Please enter your command: ')
            elif map_type == 'category':
                plot_state_map(category_events)
                print('*' * len(boundary))
                print('Generating visualization...')
                print('*' * len(boundary))
                command = input('Please enter your command: ')
            elif map_type == 'type':
                plot_type_bar(type_name, type_count, state_abbr)
                print('*' * len(boundary))
                print('Generating visualization...')
                print('*' * len(boundary))
                command = input('Please enter your command: ')
            elif map_type == 'nearby':
                print('*' * len(boundary))
                print('Generating visualization...')
                plot_nearby_sites(target_event, parking_ls, restaurant_ls)
                print('*' * len(boundary))
                command = input('Please enter your command: ')
            else:
                print('No result set available now.')
                command = input('Please re-enter your command: ')

        elif command == 'help':
            print('''
            list <stateabbr> groupby=<city/type>
                available anytime
                lists the number of events grouped by city or event type in the selected state
                valid inputs:
                    <stateabbr>: required, a two-letter state abbreviation
                    groupby=<city/type>: optional, a word of city(default) or type

            more <group_index_number>
                available only if there is an active result set of 'list' command
                lists all the event details of the selected group
                valid inputs: an integer 1-len(result_set_size)

            nearby <result_event_number>
                available only if there is an active result set of city search
                lists top 10 rated restaurants and top 5 nearest parking sturctures nearby a event
                valid inputs: an integer 1-len(result_set_size)

            plot
                available only if there is an active result set
                displays the visualization basing on the current result set in web browser

            exit
                exits the program

            help
                lists available commands (these instructions)

            ''')
            command = input('Please enter your command: ')
        else:
            print('Invalid command.')
            command = input('Invalid command. Please re-enter your command: ')

if __name__=="__main__":
    init_event_db(DB_FNAME)
    run_event_search()
