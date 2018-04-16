import plotly.plotly as py
import plotly.graph_objs as go
from plotly.graph_objs import *
from secrets import *

def plot_type_bar(type_name, type_count, state_abbr):
    trace0 = go.Bar(
        x = type_name,
        y = type_count,
        marker=dict(
            color=['rgba(139,184,199,1)', 'rgba(112,149,184,1)',
                   'rgba(217,217,217,1)', 'rgba(124,120,121,1)',
                   'rgba(76,76,76,1)']),
    )

    data = [trace0]
    layout = go.Layout(
        title='All Events in {} By Type'.format(state_abbr),
    )

    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='event-by-type')

def plot_state_map(state_events):
    event_lat = []
    event_lon = []
    event_name = []

    for e in state_events:
        if e.lat != 0:
            event_lat.append(e.lat)
            event_lon.append(e.lon)
            event_name.append(e.name)

    data = ([
        Scattermapbox(
            lat=event_lat,
            lon=event_lon,
            mode='markers',
            marker=Marker(
                size=10,
                symbol = 'circle'
            ),
            text=event_name,
            name='Event'
        )
    ])

    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000

    lat_vals = event_lat
    lon_vals = event_lon

    for v in lat_vals:
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for v in lon_vals:
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v

    lat_range = max_lat - min_lat
    lon_range = max_lon - min_lon

    if lat_range >= lon_range:
        max_range = lat_range
    else:
        max_range = lon_range

    print(max_range)

    if max_range <= 0.003:
        zoom_index = 17
    elif max_range <= 0.006:
        zoom_index = 16
    elif max_range <= 0.015:
        zoom_index = 15
    elif max_range <= 0.03:
        zoom_index = 14
    elif max_range <= 0.05:
        zoom_index = 13
    elif max_range <= 0.07:
        zoom_index = 12
    elif max_range <= 0.11:
        zoom_index = 11
    elif max_range <= 0.35:
        zoom_index = 10
    elif max_range <= 6:
        zoom_index = 6
    else:
        zoom_index = 5

    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    layout = Layout(
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center={'lat': center_lat, 'lon': center_lon },
            pitch=0,
            zoom=zoom_index
        ),
    )

    fig = dict(data=data, layout=layout)
    py.plot(fig, filename='All Events')


def plot_nearby_sites(event, parking_ls, restaurant_ls):
    event_lat = [event.lat]
    event_lon = [event.lon]
    event_name = [event.name]

    parking_lat = []
    parking_lon = []
    parking_name = []

    restaurant_lat = []
    restaurant_lon = []
    restaurant_name = []

    for p in parking_ls:
        parking_lat.append(p.lat)
        parking_lon.append(p.lon)
        parking_name.append(p.name)

    for r in restaurant_ls:
        restaurant_lat.append(r.lat)
        restaurant_lon.append(r.lon)
        restaurant_name.append(r.name)

    trace1 = Scattermapbox(
            lat=event_lat,
            lon=event_lon,
            mode='markers',
            marker=Marker(
                size=15,
                symbol = 'star',
                color='red'
            ),
            text=event_name,
            name='Event Location'
        )

    trace2 = Scattermapbox(
            lat=parking_lat,
            lon=parking_lon,
            mode='markers',
            marker=Marker(
                size=10,
                color='blue'
            ),
            text=parking_name,
            name='Parking Lot'
        )

    trace3 = Scattermapbox(
            lat=restaurant_lat,
            lon=restaurant_lon,
            mode='markers',
            marker=Marker(
                size=10,
                color='green'
            ),
            text=restaurant_name,
            name='Restaurant'
        )

    data = Data([trace1, trace2, trace3])

    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000

    lat_vals = parking_lat + restaurant_lat + event_lat
    lon_vals = parking_lon + parking_lon + event_lon

    for v in lat_vals:
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for v in lon_vals:
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v

    lat_range = max_lat - min_lat
    lon_range = max_lon - min_lon

    if lat_range >= lon_range:
        max_range = lat_range
    else:
        max_range = lon_range

    if max_range <= 0.003:
        zoom_index = 17
    elif max_range <= 0.006:
        zoom_index = 16
    elif max_range <= 0.014:
        zoom_index = 15
    elif max_range <= 0.03:
        zoom_index = 14
    elif max_range <= 0.05:
        zoom_index = 13
    elif max_range <= 0.07:
        zoom_index = 12
    else:
        zoom_index = 10

    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    layout = Layout(
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center={'lat': center_lat, 'lon': center_lon },
            pitch=0,
            zoom=zoom_index
        ),
    )

    fig = dict(data=data, layout=layout)
    py.plot(fig, filename='Nearby Sites of {}'.format(event.name))
