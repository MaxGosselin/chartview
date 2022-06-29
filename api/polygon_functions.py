from concurrent.futures import process
import pandas
from datetime import datetime
from typing import cast
from urllib3 import HTTPResponse
import json

# import requests
import pandas

# from binance import Client


# def get_cryptos_intraday_data(api_client: Client, ticker: str, date: datetime):
#     """
#     Gets intraday data on 5m timeframe from Binance API

#     Response format:
#         [
#             [
#                 1499040000000,      // Open time
#                 "0.01634790",       // Open
#                 "0.80000000",       // High
#                 "0.01575800",       // Low
#                 "0.01577100",       // Close
#                 "148976.11427815",  // Volume
#                 1499644799999,      // Close time
#                 "2434.19055334",    // Quote asset volume
#                 308,                // Number of trades
#                 "1756.87402397",    // Taker buy base asset volume
#                 "28.46694368",      // Taker buy quote asset volume
#                 "17928899.62484339" // Ignore.
#             ]
#         ]
#     """
#     start_date = get_cryptos_query_date_ranges(date)
#     # print(start_date, type(start_date))

#     data = api_client.get_historical_klines(
#         ticker, api_client.KLINE_INTERVAL_5MINUTE, start_date
#     )

#     # Iter through and drop useless data
#     cleaned_data = [
#         [
#             datetime.fromtimestamp(el[0] / 1000),
#             float(el[1]),
#             float(el[2]),
#             float(el[3]),
#             float(el[4]),
#         ]
#         for el in data
#     ]

#     data_df = pandas.DataFrame(
#         cleaned_data, columns=["datetime", "open", "high", "low", "close"]
#     )
#     # data["datetime"] = data["datetime"] // 1000
#     data_df = data_df.set_index("datetime")
#     data_df.index = pandas.to_datetime(data_df.index)

#     return data_df


def get_bars(api_client, ticker, multiplier, timespan, from_, to):
    """API wrapper fn spec: stocks_equities_aggregates(self, ticker, multiplier, timespan, from_, to,
    **query_params)"""

    # RESTClient can be used as a context manager to facilitate closing the underlying http session
    # https://requests.readthedocs.io/en/master/user/advanced/#session-objects
    # RESTClient.stocks_equities_aggregates

    aggs = api_client.get_aggs(
        ticker,
        multiplier,
        timespan,
        from_,
        to,
        adjusted=True,
        limit=500000,
    )
    # print(aggs)
    if len(aggs) > 0:
        processed = [
            {
                "open": a.open,
                "high": a.high,
                "low": a.low,
                "close": a.close,
                "volume": a.volume,
                "vwap": a.vwap,
                "timestamp": a.timestamp,
                "transactions": a.transactions,
            }
            for a in aggs
        ]
        # print(processed[:5], type(processed[0]))
        return processed
    else:
        # TODO: Handle errs cogently
        print(f"Error with ticker {ticker}")
        print(aggs.status, dir(aggs))


def __raw_to_df(rawdata: list):
    """Convert API data to pd DataFrame and set index on timestamp."""

    df = pandas.DataFrame.from_dict(rawdata)
    df = df.drop(
        ["vw", "n"],
        axis=1,
    )

    df = df.rename(
        columns={
            "o": "open",
            "h": "high",
            "l": "low",
            "c": "close",
            "t": "timestamp",
            "v": "volume",
        }
    )

    df = df.set_index("timestamp")
    df.index = (
        pandas.to_datetime(df.index, unit="ms", origin="unix")
        .tz_localize("UTC")
        .tz_convert("US/Eastern")
    )

    # Market hours only
    open_time, close_time = (
        pandas.to_datetime("9:30:00").time(),
        pandas.to_datetime("16:00:00").time(),
    )
    market_hours_mask = (df.index.time >= open_time) & (df.index.time < close_time)
    df = df[market_hours_mask]
    # print(df)
    return df
