import psycopg2


class DB:
    def __init__(self, host, database, user, password):
        self.conn = psycopg2.connect(host=host,
                                     database=database,
                                     user=user,
                                     password=password)

    def get_child_port_codes(self, parent_region):
        cur = self.conn.cursor()
        sql = """SELECT p.code FROM ports p WHERE p.parent_slug = %s;"""
        cur.execute(sql, (parent_region,))
        ports = cur.fetchall()
        cur.close()
        return [port[0] for port in ports]

    def get_child_region_slugs(self, parent_region):
        cur = self.conn.cursor()
        sql = """SELECT r.slug FROM regions r WHERE r.parent_slug = %s;"""
        cur.execute(sql, (parent_region,))
        regions = cur.fetchall()
        cur.close()
        return [region[0] for region in regions]

    def get_daily_prices(self, orig_code, dest_code, day):
        cur = self.conn.cursor()
        sql = """SELECT p.price FROM prices p
                 WHERE p.orig_code = %s AND p.dest_code = %s AND p."day" = %s;"""
        cur.execute(sql, (orig_code, dest_code, day))
        prices = cur.fetchall()
        cur.close()
        return [price[0] for price in prices]

    def get_port(self, orig_code):
        cur = self.conn.cursor()
        sql = """SELECT p.code FROM ports p
                    where p.code = %s"""
        cur.execute(sql, (orig_code,))
        port = cur.fetchone()
        cur.close()
        return port

    def close(self):
        self.conn.close()
