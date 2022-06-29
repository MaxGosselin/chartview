import time
from flask import Flask, request
from polygon import RESTClient
from api_key import API_KEY
from polygon_functions import get_bars

app = Flask(__name__)
poly_client = RESTClient(API_KEY)

RESOLUTIONS = {
    "5m": (5, "minute"),
    "15m": (15, "minute"),
    "30m": (30, "minute"),
    "1h": (60, "minute"),
    "1d": (1, "day"),
}


@app.route("/api/chart")
def get_ct():
    ticker = request.args.get("ticker")
    to = request.args.get("to")
    from_ = request.args.get("from")
    res = RESOLUTIONS[request.args.get("res")]

    print("REQUESTED:", ticker, to, from_, res)

    return {
        "chart": get_bars(poly_client, ticker, res[0], res[1], from_, to),
        # "chart": get_bars(
        #     poly_client, "AAPL", 60, "minute", "2022-04-04", "2022-04-04"
        # ),
    }
