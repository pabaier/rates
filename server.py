from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def base():
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    origin = request.args.get('origin')
    destination = request.args.get('destination')

    print(date_from, date_to, origin, destination)
    return {
        "message": "hello, world!"
    }