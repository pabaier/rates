import unittest

from werkzeug.datastructures import MultiDict

from server import process_query_params


class TestProcessQueryParams(unittest.TestCase):

    def setUp(self) -> None:
        self.error = lambda field: (
            {"error": f"{field} incorrect range or format. Make sure it is formatted YYYY-MM-DD"}, 400)

    def test_all_fields_included(self):
        # arrange
        date_from, date_to, origin, destination = "from", "to", "here", "there"
        query = MultiDict([('date_from', date_from), ('date_to', date_to), ('origin', origin), ('destination', destination)])

        # act
        res = process_query_params(query)

        # assert
        expected = ([], date_from, date_to, origin, destination)
        self.assertEqual(res, expected)

    def test_missing_fields(self):
        # arrange
        date_from, date_to, origin, destination = "from", "to", "here", "there"
        query = MultiDict([('date_from', date_from), ('date_to', date_to), ('origin', origin), ('destination', destination)])
        included_fields = [{'included': (date_from, date_to, origin, None), 'missing': ['destination']},
                           {'included': (date_from, date_to, None, destination), 'missing': ['origin']},
                           {'included': (date_from, None, origin, destination), 'missing': ['date_to']},
                           {'included': (None, date_to, origin, destination), 'missing': ['date_from']},
                           {'included': (None, date_to, origin, None), 'missing': ['date_from', 'destination']}
                           ]
        for test in included_fields:
            included: tuple[str|None, str|None, str|None, str|None] = test['included']
            missing = test['missing']
            for miss in missing:
                query.pop(miss)

            # act
            res = process_query_params(query)
            query = {'date_from': date_from, 'date_to': date_to, 'origin': origin, 'destination': destination}

            # assert
            expected = (missing,) + included
            self.assertEqual(res, expected)


if __name__ == '__main__':
    unittest.main()
