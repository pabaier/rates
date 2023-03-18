import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from flask import Flask, request
from werkzeug.datastructures import MultiDict

from database import DB

app = Flask(__name__)
load_dotenv()
db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']
db_host = os.environ['DB_HOST']
db_database = os.environ['DB_DATABASE']

db = None


def get_sub_ports(region: str) -> list:
    """
    gets all the ports within a region
    :param region: region slug
    :return: list of port codes
    """
    ports = []
    regions_left = [region]
    while len(regions_left) > 0:
        next_region = regions_left.pop(0)

        # get the region's ports
        region_ports = db.get_child_port_codes(next_region)
        ports += region_ports

        # get the region's child regions
        child_regions = db.get_child_region_slugs(next_region)
        regions_left += child_regions

    return ports


def create_date_range(date_from: str, date_to: str) -> dict:
    """
    creates a list of dates of each day between [date_from and date_to] (inclusive)
    :param date_from: start date
    :param date_to: end date
    :return: dictionary of {error: bool, value}
    """
    try:
        date_start = datetime.strptime(date_from, '%Y-%m-%d')
    except ValueError:
        return {"error": True,
                "value": ({"error": "date_from incorrect range or format. Make sure it is formatted YYYY-MM-DD"}, 400)}
    except Exception as e:
        return {"error": True, "value": ({"error": f"date_from error: {str(e)}"}, 400)}
    try:
        date_end = datetime.strptime(date_to, '%Y-%m-%d')
    except ValueError:
        return {"error": True,
                "value": ({"error": "date_to incorrect range or format. Make sure it is formatted YYYY-MM-DD"}, 400)}
    except Exception as e:
        return {"error": True, "value": ({"error": f"date_to error: {str(e)}"}, 400)}
    dates = [date_start + timedelta(days=days) for days in range((date_end - date_start).days + 1)]
    return {"error": False, "value": dates}


def process_query_params(args: MultiDict[str, str]) -> (str, str, str, str, str):
    """
    processes the request's query parameters
    :param args: query parameters
    :return: errors, date_from value, date_to value, origin value, destination value
    """
    err = []
    date_from = args.get('date_from')
    if not date_from:
        err.append('date_from')
    date_to = args.get('date_to')
    if not date_to:
        err.append('date_to')
    origin = args.get('origin')
    if not origin:
        err.append('origin')
    destination = args.get('destination')
    if not destination:
        err.append('destination')
    return err, date_from, date_to, origin, destination

@app.route("/rates")
def rates():
    """
    Gets the average price per day between an origin and destination for a specified date range

    Process query params
    Set the date range
    Check from and to ports
    Get all origin and destination ports
    Get prices between each origin and destination port
    """

    query_err, date_from, date_to, origin, destination = process_query_params(request.args)
    if query_err:
        return {"error": f"{query_err} params required"}, 400


    # get date range
    dates_range = create_date_range(date_from, date_to)
    if dates_range['error']: return dates_range['value']

    origin_is_port = origin.isupper()
    destination_is_port = destination.isupper()

    # make sure origin and destination are valid ports (if they are ports)
    # we can filter out if they are bad region values based on their sub region/ports below
    if origin_is_port and not db.get_port(origin):
        return {"error": f"invalid origin port {origin}"}, 400
    if destination_is_port and not db.get_port(destination):
        return {"error": f"invalid destination port {destination}"}, 400

    # get ports
    origin_ports = [origin] if origin.isupper() else get_sub_ports(origin)
    destination_ports = [destination] if destination.isupper() else get_sub_ports(destination)

    # get_sub_ports returns nothing, which means the origin/destination region was bad
    if not origin_ports:
        return {"error": f"invalid origin region {origin}"}, 400
    if not destination_ports:
        return {"error": f"invalid destination region {destination}"}, 400

    results = []
    for date in dates_range['value']:
        # for any given day, add up all the prices between all the origin and destination ports
        date_string = date.strftime('%Y-%m-%d')
        prices = []
        for origin_port in origin_ports:
            for destination_port in destination_ports:
                prices += db.get_daily_prices(origin_port, destination_port, date_string)
        results.append({
            "day": date_string,
            "average_price": None if len(prices) < 3 else round(sum(prices) / len(prices))
        })

    return results


if __name__ == '__main__':
    db = DB(db_host, db_database, db_user, db_password)
    app.run(host="localhost", port=8080, debug=True)
    db.close()
