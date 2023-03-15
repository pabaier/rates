from datetime import datetime, timedelta

from flask import Flask, request

from db import DB

app = Flask(__name__)
db = DB('localhost', 'postgres', 'postgres', 'ratestask')


def get_sub_ports(region):
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
    if origin_is_port and not db.get_port(origin):
        return {"error": f"invalid origin port {origin}"}, 400
    if destination_is_port and not db.get_port(destination):
        return {"error": f"invalid destination port {destination}"}, 400

    # get ports
    origin_ports = [origin] if origin.isupper() else get_sub_ports(origin)
    destination_ports = [destination] if destination.isupper() else get_sub_ports(destination)

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
                prices += db.get_daily_prices(origin_port, destination_port, date_string)
        results.append({
            "day": date_string,
            "average_price": None if len(prices) < 3 else round(sum(prices) / len(prices))
        })

    return results


if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=True)
    db.close()
