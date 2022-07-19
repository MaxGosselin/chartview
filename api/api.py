import time
from flask import Flask, request
from polygon import RESTClient
from api_key import API_KEY
from polygon_functions import get_bars

app = Flask(__name__)
poly_client = RESTClient(API_KEY)

RESOLUTIONS = {
    "1m": (1, "minute"),
    "5m": (5, "minute"),
    "15m": (15, "minute"),
    "30m": (30, "minute"),
    "1h": (60, "minute"),
    "1d": (1, "day"),
    "1wk": (1, "week"),
    "1mo": (1, "month"),
}


@app.route("/api/chart")
def get_ct():
    ticker = request.args.get("ticker")
    to = request.args.get("to")
    from_ = request.args.get("from")
    res = RESOLUTIONS[request.args.get("res")]
    ext_hours = request.args.get("ah")
    ext_hours = True if ext_hours == "true" else False

    print("REQUESTED:", ticker, from_, to, res)
    api_response = get_bars(poly_client, ticker, res[0], res[1], from_, to, ext_hours)

    return {
        "response_status": api_response[1],
        "chart": api_response[0],
        # "chart": get_bars(
        #     poly_client, "AAPL", 60, "minute", "2022-04-04", "2022-04-04"
        # ),
    }
