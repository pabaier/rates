import unittest

from unittest.mock import patch
from test.mock_database import MockDB
from server import app


mock_db = MockDB()

@patch('server.db', mock_db)
class TestServer(unittest.TestCase):

    def test_origin_and_dest_ports(self):
        # arrange
        origin_port = "ABCDE"
        destination_port = "VWXYZ"
        start_date="2016-01-01"
        end_date = "2016-01-03"

        def daily_prices_func(origin, dest, day):
            match day:
                case "2016-01-01": return [121, 122, 123]
                case "2016-01-02": return [456]
                case "2016-01-03": return [789, 790, 791, 792]
                case _: return [701]

        mock_db.set_port(lambda x: (True,)) # inputs are ports
        # mock_db.set_child_port_codes() # not used
        # mock_db.set_child_region_slugs() # not used
        mock_db.set_daily_prices(daily_prices_func)

        # act
        response = app.test_client().get(f'/rates?date_from={start_date}&date_to={end_date}&origin={origin_port}&destination={destination_port}')

        # assert
        expected = [{'average_price': 122, 'day': '2016-01-01'}, {'average_price': None, 'day': '2016-01-02'}, {'average_price': 790, 'day': '2016-01-03'}]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected)

    def test_origin_port_and_dest_region(self):
        # arrange
        origin_port = "ABCDE"
        destination_region = "a_region"
        start_date="2016-01-01"
        end_date = "2016-01-03"

        def daily_prices_func(origin, dest, day):
            match origin, dest, day:
                case "ABCDE", "VWXYZ", "2016-01-01": return [121, 122, 123]
                case "ABCDE", "VWXYZ", "2016-01-02": return [456]
                case "ABCDE", "VWXYZ", "2016-01-03": return [789, 790, 791, 792]
                case _: return [701]

        mock_db.set_port(lambda x: (True,)) # input is port
        mock_db.set_child_port_codes(lambda x: ["VWXYZ"]) # only port in a_region is VWXYZ
        mock_db.set_child_region_slugs(lambda x: []) # not child regions in region
        mock_db.set_daily_prices(daily_prices_func)

        # act
        response = app.test_client().get(f'/rates?date_from={start_date}&date_to={end_date}&origin={origin_port}&destination={destination_region}')

        # assert
        expected = [{'average_price': 122, 'day': '2016-01-01'}, {'average_price': None, 'day': '2016-01-02'}, {'average_price': 790, 'day': '2016-01-03'}]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected)

    def test_origin_region_and_dest_port(self):
        # arrange
        origin_region = "a_region"
        destination_port = "VWXYZ"
        start_date="2016-01-01"
        end_date = "2016-01-03"

        def daily_prices_func(origin, dest, day):
            match origin, dest, day:
                case "ABCDE", "VWXYZ", "2016-01-01": return [121, 122, 123]
                case "ABCDE", "VWXYZ", "2016-01-02": return [456]
                case "ABCDE", "VWXYZ", "2016-01-03": return [789, 790, 791, 792]
                case _: return [701]

        mock_db.set_port(lambda x: (True,)) # input is port
        mock_db.set_child_port_codes(lambda x: ["ABCDE"]) # only port in a_region is ABCDE
        mock_db.set_child_region_slugs(lambda x: []) # not child regions in region
        mock_db.set_daily_prices(daily_prices_func)

        # act
        response = app.test_client().get(f'/rates?date_from={start_date}&date_to={end_date}&origin={origin_region}&destination={destination_port}')

        # assert
        expected = [{'average_price': 122, 'day': '2016-01-01'}, {'average_price': None, 'day': '2016-01-02'}, {'average_price': 790, 'day': '2016-01-03'}]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected)

    def test_origin_region_and_dest_region(self):
        # arrange
        origin_region = "a_region"
        destination_region = "b_region"
        start_date="2016-01-01"
        end_date = "2016-01-03"

        def child_ports_func(region):
            match region:
                case "a_region": return ["ABCDE"]
                case "b_region": return ["VWXYZ"]
                case "c_region": return ["PQRST"]
                case _: return ["LMNOP"]

        def child_region_func(region):
            match region:
                case "b_region": return ["c_region"]
                case _: return []

        def daily_prices_func(origin, dest, day):
            match origin, dest, day:
                case "ABCDE", "VWXYZ", "2016-01-01": return [121, 122, 123]
                case "ABCDE", "PQRST", "2016-01-01": return [124, 125]
                case "ABCDE", "VWXYZ", "2016-01-02": return [456]
                case "ABCDE", "PQRST", "2016-01-03": return [789, 790, 791, 792]
                case _: return []

        mock_db.set_port(lambda x: (True,)) # input is port (not used)
        mock_db.set_child_port_codes(child_ports_func)
        mock_db.set_child_region_slugs(child_region_func)
        mock_db.set_daily_prices(daily_prices_func)

        # act
        response = app.test_client().get(f'/rates?date_from={start_date}&date_to={end_date}&origin={origin_region}&destination={destination_region}')

        # assert
        expected = [{'average_price': 123, 'day': '2016-01-01'}, {'average_price': None, 'day': '2016-01-02'}, {'average_price': 790, 'day': '2016-01-03'}]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected)

    def test_bad_origin_port_query_param(self):
        # arrange
        origin_port = "ABCD"
        destination_port = "VWXYZ"
        start_date="2016-01-01"
        end_date = "2016-01-03"

        mock_db.set_port(lambda x: (True,) if x == "ABCDE" else None) # ABCDE is only acceptable port
        # mock_db.set_child_port_codes() # not used
        # mock_db.set_child_region_slugs() # not used
        # mock_db.set_daily_prices() # not used

        # act
        response = app.test_client().get(f'/rates?date_from={start_date}&date_to={end_date}&origin={origin_port}&destination={destination_port}')

        # assert
        expected = {'error': f'invalid origin port {origin_port}'}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, expected)

    def test_bad_dest_port_query_param(self):
        # arrange
        origin_port = "ABCDE"
        destination_port = "VWXY"
        start_date="2016-01-01"
        end_date = "2016-01-03"

        mock_db.set_port(lambda x: (True,) if x == "ABCDE" else None) # ABCDE is only acceptable port
        # mock_db.set_child_port_codes() # not used
        # mock_db.set_child_region_slugs() # not used
        # mock_db.set_daily_prices() # not used

        # act
        response = app.test_client().get(f'/rates?date_from={start_date}&date_to={end_date}&origin={origin_port}&destination={destination_port}')

        # assert
        expected = {'error': f'invalid destination port {destination_port}'}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, expected)

    def test_missing_query_param(self):
        # arrange
        missing_origin = f'/rates?date_from=2016-01-01&date_to=2016-01-10&destination=VWXYZ'
        missing_dest = f'/rates?date_from=2016-01-01&date_to=2016-01-10&origin=ABCDE'
        missing_from_date = f'/rates?date_to=2016-01-10&origin=ABCDE&destination=VWXYZ'
        missing_to_date = f'/rates?date_from=2016-01-01&origin=ABCDE&destination=VWXYZ'
        tests = [(missing_origin, "origin"),
                 (missing_dest, "destination"),
                 (missing_from_date, "date_from"),
                 (missing_to_date, "date_to")]

        for test, param in tests:
            # act
            response = app.test_client().get(test)

            # assert
            expected = {"error": f"{param} param required"}
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json, expected)


if __name__ == '__main__':
    unittest.main()

