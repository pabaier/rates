class MockDB:
    def __init__(self):
        self.get_child_port_codes_function = lambda x : []
        self.get_child_region_slugs_function = lambda x : []
        self.get_daily_prices_function = lambda x, y, z : []
        self.get_port_function = lambda x : []

    def get_child_port_codes(self, parent_region):
        return self.get_child_port_codes_function(parent_region)

    def get_child_region_slugs(self, parent_region):
        return self.get_child_region_slugs_function(parent_region)

    def get_daily_prices(self, orig_code, dest_code, day):
        return self.get_daily_prices_function(orig_code, dest_code, day)

    def get_port(self, orig_code):
        return self.get_port_function(orig_code)

    def set_child_port_codes(self,func):
        self.get_child_port_codes_function = func

    def set_child_region_slugs(self, func):
        self.get_child_region_slugs_function = func

    def set_daily_prices(self, func):
        self.get_daily_prices_function = func

    def set_port(self, func):
        self.get_port_function = func

    def close(self):
        pass
