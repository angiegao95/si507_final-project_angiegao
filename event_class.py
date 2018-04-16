class Event():
    def __init__(self, eventtype, name, date, desc, address, lat, lon):
        self.type = eventtype
        self.name = name
        self.date = date
        self.desc = desc
        self.address = address
        self.lat = lat
        self.lon = lon

    def __str__(self):
        event_str = '[{}]{}({}): {}'.format(self.type, self.name, self.date, self.address)
        return event_str

class Restaurant():
    def __init__(self, name, rate, lat, lon, address, city, state):
        self.name = name
        self.rate = rate

        self.address = address
        self.city = city
        self.state = state
        self.lat = lat
        self.lon = lon
    def __str__(self):
        rest_str = '{}({}): {}, {}, {}'.format(self.name, self.rate, self.address, self.city, self.state)
        return rest_str

class ParkingStructure():
    def __init__(self, name, address, lat, lon):
        self.name = name
        self.address = address
        self.lat = lat
        self.lon = lon
    def __str__(self):
        return '{}: {}'.format(self.name, self.address)
