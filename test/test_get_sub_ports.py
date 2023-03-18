import unittest
from unittest.mock import patch, MagicMock

from server import get_sub_ports
from database import DB

DB.__init__ = lambda x: None
mock_db = DB()


@patch('server.db', mock_db)
class TestGetSubPorts(unittest.TestCase):

    def test_one_port_in_region(self):
        # arrange
        region = 'a_region'
        port = "ABCDE"

        mock_db.get_child_port_codes = MagicMock(return_value=[port])
        mock_db.get_child_region_slugs = MagicMock(return_value=[])

        # act
        res = get_sub_ports(region)

        # assert
        self.assertEqual(res, [port])

    def test_multiple_ports_in_region(self):
        # arrange
        region = 'a_region'
        ports = ["ABCDE", "DEFGH"]

        mock_db.get_child_port_codes = MagicMock(return_value=ports)
        mock_db.get_child_region_slugs = MagicMock(return_value=[])

        # act
        res = get_sub_ports(region)

        # assert
        self.assertEqual(res, ports)

    def test_sub_region_in_region(self):
        # arrange
        region = 'a_region'
        sub_region = 'b_region'
        a_ports = ["A1111", "A2222"]
        b_ports = ['B1111']

        def child_ports_func(region):
            match region:
                case 'a_region':
                    return a_ports
                case 'b_region':
                    return b_ports

        def child_regions_func(region):
            match region:
                case 'a_region':
                    return [sub_region]
                case 'b_region':
                    return []

        mock_db.get_child_port_codes = MagicMock(side_effect=child_ports_func)
        mock_db.get_child_region_slugs = MagicMock(side_effect=child_regions_func)

        # act
        res = get_sub_ports(region)

        # assert
        self.assertEqual(res, a_ports + b_ports)

    def test_multi_sub_regions_in_region(self):
        # arrange
        region = 'a_region'
        a_sub_regions = ['b_region', 'c_region']
        b_sub_regions = ['d_region', 'e_region']
        c_sub_regions = ['f_region']
        d_sub_regions = []
        e_sub_regions = []
        f_sub_regions = []
        a_ports = ["A1111", "A2222"]
        b_ports = ['B1111']
        c_ports = ['C1111', 'C2222', 'C3333']
        d_ports = ['D1111']
        e_ports = ['E1111']
        f_ports = ['F1111']

        def child_ports_func(region):
            match region:
                case 'a_region':
                    return a_ports
                case 'b_region':
                    return b_ports
                case 'c_region':
                    return c_ports
                case 'd_region':
                    return d_ports
                case 'e_region':
                    return e_ports
                case 'f_region':
                    return f_ports

        def child_regions_func(region):
            match region:
                case 'a_region':
                    return a_sub_regions
                case 'b_region':
                    return b_sub_regions
                case 'c_region':
                    return c_sub_regions
                case 'd_region':
                    return d_sub_regions
                case 'e_region':
                    return e_sub_regions
                case 'f_region':
                    return f_sub_regions

        mock_db.get_child_port_codes = MagicMock(side_effect=child_ports_func)
        mock_db.get_child_region_slugs = MagicMock(side_effect=child_regions_func)

        # act
        res = get_sub_ports(region)

        # assert
        self.assertEqual(res, a_ports + b_ports + c_ports + d_ports + e_ports + f_ports)


if __name__ == '__main__':
    unittest.main()
