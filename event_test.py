import unittest
from run_event_search import *

class TestDatabase(unittest.TestCase):
    def test_event_table(self):
        conn = sqlite.connect(DB_FNAME)
        cur = conn.cursor()

        sql = 'SELECT City FROM Events WHERE State="MI"'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Ann Arbor',), result_list)
        self.assertEqual(len(result_list), 100)

        sql = '''
            SELECT *
            FROM Events
            WHERE City="Ann Arbor"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 3)
        self.assertEqual(result_list[0][2], '2018-05-2')

        conn.close()

    def test_type_table(self):
        conn = sqlite.connect(DB_FNAME)
        cur = conn.cursor()

        sql = 'SELECT TypeName FROM Types'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Music',), result_list)
        self.assertEqual(len(result_list), 5)

        conn.close()

    def test_joins(self):
        conn = sqlite.connect(DB_FNAME)
        cur = conn.cursor()

        sql = '''
            SELECT T.TypeName
            FROM Events AS E
            	JOIN EventType AS ET ON E.Id = ET.EventId
            	JOIN Types AS T ON ET.TypeId = T.Id
            WHERE E.City = 'Lansing'
        '''
        results = cur.execute(sql)
        result_list = results.fetchone()
        self.assertEqual(result_list[0], 'Commercial')

class TestClass(unittest.TestCase):
    def test_event_class(self):
        sample = Event(['Craft','Commercial'],'Strut Up Detroit 2018','2018-04-20','sample','Royal Oak Farmers Market', 42.489412, -83.1411249)
        self.assertEqual(sample.desc, 'sample')
        self.assertEqual(sample.lat, 42.489412)

    def test_restaurant_class(self):
        sample = Restaurant('Superior Fish', 3.5, 0, 0, 'Sample Address', 'Sample City', 'MI')
        self.assertEqual(sample.address, 'Sample Address')
        self.assertEqual(sample.__str__(), 'Superior Fish(3.5): Sample Address, Sample City, MI')

    def test_parking_class(self):
        sample = ParkingStructure('P11', 'Sample Address', 0, 0)
        self.assertEqual(sample.lat, 0)
        self.assertEqual(sample.__str__, 'P11: Sample Address')

class TestRestaurantSearch(unittest.TestCase):
    def test_restaurant_search(self):
        sample = Event(['Craft','Commercial'],'Strut Up Detroit 2018','2018-04-20','sample','Royal Oak Farmers Market', 42.489412, -83.1411249)
        restaurant_ls = search_nearby_restaurants(sample)
        self.assertEqual(len(restaurant_ls), 10)
        self.assertEqual(restaurant_ls[0].name, 'Hot Diggity Dog')
        self.assertEqual(restaurant_ls[5].rate, 3.5)


class TestParkingSearch(unittest.TestCase):
    def test_parking_search(self):
        sample = Event(['Craft','Commercial'],'Strut Up Detroit 2018','2018-04-20','sample','Royal Oak Farmers Market', '42.489412', '-83.1411249')
        restaurant_ls = search_nearby_parkings(sample)
        self.assertEqual(len(restaurant_ls), 5)
        self.assertEqual(restaurant_ls[1].name, 'Farmers Market Parking Lot P11')
        self.assertEqual(restaurant_ls[4].address, '300N Main St, Royal Oak')

unittest.main()
