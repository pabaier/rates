import unittest
from datetime import datetime

from server import create_date_range


class TestCreateDateRange(unittest.TestCase):

    def setUp(self) -> None:
        self.error = lambda field: (
        {"error": f"{field} incorrect range or format. Make sure it is formatted YYYY-MM-DD"}, 400)

    def test_correctly_create_date_range(self):
        res = create_date_range("2016-01-01", "2016-01-10")
        expected = []
        for i in range(1, 10):
            expected.append(datetime.strptime(f"2016-01-0{i}", '%Y-%m-%d'))
        expected.append(datetime.strptime(f"2016-01-10", '%Y-%m-%d'))
        self.assertFalse(res['error'])
        self.assertEqual(res['value'], expected)

    def test_error_on_bad_from_create_date_range(self):
        res = create_date_range("2016-0101", "2016-01-10")
        self.assertTrue(res['error'])
        self.assertEqual(res['value'], self.error("date_from"))

    def test_error_on_bad_to_create_date_range(self):
        res = create_date_range("2016-01-01", "2016-0110")
        self.assertTrue(res['error'])
        self.assertEqual(res['value'], self.error("date_to"))


if __name__ == '__main__':
    unittest.main()
