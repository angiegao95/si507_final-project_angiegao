import sqlite3 as sqlite
from sqlite3 import Error
from event_class import *

DB_FNAME = 'event_db.sqlite'

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
            'Description' TEXT NOT NULL,
            'Latitude' FLOAT NULL,
            'Longitude' FLOAT NULL
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

def insert_event_to_db(event_type, event_title, event_date, event_desc, event_address, event_city, event_state, event_lat, event_lon):
    global DB_FNAME
    conn = sqlite.connect(DB_FNAME)
    cur = conn.cursor()
    insert_statement = '''
        INSERT INTO Events (Name, Date, City, State, Address, Description, Latitude, Longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    '''
    params = (event_title, event_date, event_city, event_state, event_address, event_desc, event_lat, event_lon)
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

def check_state_db(state_abbr):
    global DB_FNAME
    conn = sqlite.connect(DB_FNAME)
    cur = conn.cursor()
    check_statement = '''
        SELECT COUNT(*)
        FROM Events
        WHERE Events.State = ?
    '''
    params = (state_abbr,)
    cur.execute(check_statement, params)
    result = cur.fetchone()[0]
    conn.close()

    if result == 0:
        ava = False
    else:
        ava = True
    return ava


def group_event_by_city(state_abbr):
    global DB_FNAME
    conn = sqlite.connect(DB_FNAME)
    cur = conn.cursor()
    group_statement = '''
        SELECT City, COUNT(*)
        FROM Events
        WHERE Events.State = ?
        GROUP BY Events.City
    '''
    params = (state_abbr,)
    cur.execute(group_statement, params)
    result = cur.fetchall()
    conn.close()
    return result

def group_event_by_type(state_abbr):
    global DB_FNAME
    conn = sqlite.connect(DB_FNAME)
    cur = conn.cursor()
    group_statement = '''
        SELECT T.TypeName, COUNT(*)
        FROM Events As E
        	JOIN EventType As ET ON E.Id = ET.EventId
        	JOIN Types AS T ON ET.TypeId = T.Id
        WHERE E.State = ?
        GROUP BY T.TypeName
    '''
    params = (state_abbr,)
    cur.execute(group_statement, params)
    result = cur.fetchall()
    conn.close()
    return result

def search_state_event(state_abbr):
    global DB_FNAME
    fetched_events = []
    conn = sqlite.connect(DB_FNAME)
    cur = conn.cursor()
    search_statement = '''
        SELECT Name, [Date], Address, Description, Latitude, Longitude
        FROM Events
        WHERE State = ?
    '''
    params = (state_abbr,)
    cur.execute(search_statement, params)
    result = cur.fetchall()

    for row in result:
        event_type = []

        type_statement = '''
            SELECT T.TypeName
            FROM EventType As ET
            	JOIN Events AS E ON E.Id = ET.EventId
            	JOIN Types AS T ON ET.TypeId = T.Id
            WHERE E.Name = ?
        '''
        params = (row[0],)
        cur.execute(type_statement, params)
        all_types = cur.fetchall()
        for t in all_types:
            event_type.append(t[0])

        fetched_events.append(Event(event_type, row[0], row[1], row[3], row[2], row[4], row[5]))
    conn.close()
    return fetched_events

def search_category_event(category, search_base):
    global DB_FNAME
    fetched_events = []

    conn = sqlite.connect(DB_FNAME)
    cur = conn.cursor()
    if search_base == 'city':
        search_statement = '''
            SELECT Name, [Date], Address, Description, Latitude, Longitude
            FROM Events
            WHERE City = ?
        '''
    else:
        search_statement = '''
            SELECT Name, [Date], Address, Description, Latitude, Longitude
            FROM Events AS E
            	JOIN EventType AS ET ON E.Id = ET.EventId
            	JOIN Types AS T ON T.Id = ET.TypeId
            WHERE T.TypeName = ?
        '''
    params = (category,)
    cur.execute(search_statement, params)
    result = cur.fetchall()

    for row in result:
        event_type = []

        type_statement = '''
            SELECT T.TypeName
            FROM EventType As ET
            	JOIN Events AS E ON E.Id = ET.EventId
            	JOIN Types AS T ON ET.TypeId = T.Id
            WHERE E.Name = ?
        '''
        params = (row[0],)
        cur.execute(type_statement, params)
        all_types = cur.fetchall()
        for t in all_types:
            event_type.append(t[0])

        fetched_events.append(Event(event_type, row[0], row[1], row[3], row[2], row[4], row[5]))
    conn.close()
    return fetched_events
