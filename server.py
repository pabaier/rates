from datetime import datetime, timedelta

import psycopg2
from flask import Flask, request

app = Flask(__name__)


def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='postgres',
                            user='postgres',  # os.environ['postgres'],
                            password='ratestask')  # os.environ['DB_PASSWORD'])
    return conn


# ------------ DB ------------------------------------------------------
def get_child_port_codes(parent_region, conn):
    cur = conn.cursor()
    sql = """SELECT p.code FROM ports p WHERE p.parent_slug = %s;"""
    cur.execute(sql, (parent_region,))
    ports = cur.fetchall()
    cur.close()
    return [port[0] for port in ports]


def get_child_region_slugs(parent_region, conn):
    cur = conn.cursor()
    sql = """SELECT r.slug FROM regions r WHERE r.parent_slug = %s;"""
    cur.execute(sql, (parent_region,))
    regions = cur.fetchall()
    cur.close()
    return [region[0] for region in regions]


def get_daily_prices(orig_code, dest_code, day, conn):
    cur = conn.cursor()
    sql = """SELECT p.price FROM public.prices p
             WHERE p.orig_code = %s AND p.dest_code = %s AND p."day" = %s;"""
    cur.execute(sql, (orig_code, dest_code, day))
    prices = cur.fetchall()
    cur.close()
    return [price[0] for price in prices]


def get_port(orig_code, conn):
    cur = conn.cursor()
    sql = """SELECT p.code FROM ports p
                where p.code = %s"""
    cur.execute(sql, (orig_code,))
    port = cur.fetchone()
    cur.close()
    return port

# ----------------------------------------------------------------------

def get_sub_ports(region, conn):
    ports = []
    regions_left = [region]
    while len(regions_left) > 0:
        next_region = regions_left.pop(0)

        # get the region's ports
        region_ports = get_child_port_codes(next_region, conn)
        ports += region_ports

        # get the region's child regions
        child_regions = get_child_region_slugs(next_region, conn)
        regions_left += child_regions

    return ports


@app.route("/rates")
def base():
    """
    Gets the average price per day between an origin and destination for a specified date range

    Process query params
    Set the date range
    Check from and to ports
    Get all origin and destination ports
    Get prices between each origin and destination port
    """
    conn = get_db_connection()

    # get query params
    date_from = request.args.get('date_from')
    if not date_from:
        return {"error": "date_from param required"}, 400
    date_to = request.args.get('date_to')
    if not date_to:
        return {"error": "date_to param required"}, 400
    origin = request.args.get('origin')
    if not origin:
        return {"error": "origin param required"}, 400
    destination = request.args.get('destination')
    if not destination:
        return {"error": "destination param required"}, 400

    # get date range
    try:
        date_start = datetime.strptime(date_from, '%Y-%m-%d')
    except ValueError:
        return {"error": "date_from incorrect range or format. Make sure it is formatted YYYY-MM-DD"}, 400
    except Exception as e:
        return {"error": f"date_from error: {str(e)}"}, 400
    try:
        date_end = datetime.strptime(date_to, '%Y-%m-%d')
    except ValueError:
        return {"error": "date_to incorrect range or format. Make sure it is formatted YYYY-MM-DD"}, 400
    except Exception as e:
        return {"error": f"date_to error: {str(e)}"}, 400
    dates = [date_start + timedelta(days=days) for days in range((date_end - date_start).days + 1)]

    origin_is_port = origin.isupper()
    destination_is_port = destination.isupper()

    # make sure origin and destination are valid ports (if they are ports)
    # we can filter out if they are bad region values based on their sub region/ports below
    if origin_is_port and not get_port(origin, conn):
        return {"error": f"invalid origin port {origin}"}, 400
    if destination_is_port and not get_port(destination, conn):
        return {"error": f"invalid destination port {destination}"}, 400

    # get ports
    origin_ports = [origin] if origin.isupper() else get_sub_ports(origin, conn)
    destination_ports = [destination] if destination.isupper() else get_sub_ports(destination, conn)

    if not origin_ports:
        return {"error": f"invalid origin port {origin}"}, 400
    if not destination_ports:
        return {"error": f"invalid destination port {destination}"}, 400

    results = []
    for date in dates:
        # for any given day, add up all the prices between all the origin and destination ports
        date_string = date.strftime('%Y-%m-%d')
        prices = []
        for origin_port in origin_ports:
            for destination_port in destination_ports:
                prices += get_daily_prices(origin_port, destination_port, date_string, conn)
        results.append({
            "day": date_string,
            "average_price": None if len(prices) < 3 else round(sum(prices) / len(prices))
        })

    conn.close()
    return results


if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=True)
