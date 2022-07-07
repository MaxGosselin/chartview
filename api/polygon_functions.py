from concurrent.futures import process
import pandas as pd
import numpy as np
from datetime import datetime
from typing import cast
from urllib3 import HTTPResponse
import json

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

#     data_df = pd.DataFrame(
#         cleaned_data, columns=["datetime", "open", "high", "low", "close"]
#     )
#     # data["datetime"] = data["datetime"] // 1000
#     data_df = data_df.set_index("datetime")
#     data_df.index = pd.to_datetime(data_df.index)

#     return data_df


def get_bars(api_client, ticker, multiplier, timespan, from_, to, ext_hours=False):
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
        raw=True,
    )

    if aggs.status < 400:
        # processed = [
        #     {
        #         "open": a.open,
        #         "high": a.high,
        #         "low": a.low,
        #         "close": a.close,
        #         "volume": a.volume,
        #         "vwap": a.vwap,
        #         "timestamp": a.timestamp,
        #         "transactions": a.transactions,
        # "bar_range": round(, 4) * 100,
        #     }
        #     for a in aggs
        # ]

        aggs_df = adjust_timeframe(aggs, ext_hours)
        # print(processed[:5], type(processed[0]))
        aggs_df = calculate_stuff(aggs_df)
        # print(aggs_df)
        return aggs_df.to_dict("records"), aggs.status
    else:
        # TODO: Handle errs cogently
        print(f"Error with ticker {ticker}")
        print(aggs.status, dir(aggs))
        return aggs.message, aggs.status


def calculate_stuff(df):
    def weighted_vwap(grp):
        def compute_from_window(wdow):
            wv = df.loc[wdow.index]
            # print(wv[["vwap", "volume"]])
            avg = np.average(wv["vwap"], weights=wv["volume"])
            print(avg)
            return avg

        grp["true_vwap"] = (
            grp["vwap"]
            .rolling(window=len(df), min_periods=1)
            .apply(compute_from_window)
        )

        print(type(grp), grp)
        return grp

        # pd.Series()
        #  g.apply(lambda x: pd.Series(np.average(x[["var1", "var2"]], weights=x["weights"], axis=0), ["var1", "var2"]))

    # print(df.groupby(df.index.date))
    df["true_vwap"] = df.groupby(df.index.floor("d"))[["vwap", "volume"]].apply(
        weighted_vwap
    )["true_vwap"]
    # print(x["true_vwap"])
    #  = x
    df["bar_range"] = ((df.high / df.low) - 1) * 100
    print(df.head(10))

    return df


def adjust_timeframe(rawdata: list, ext_hours):
    """Convert API data to pd DataFrame and set index on timestamp."""

    df = pd.DataFrame(json.loads(rawdata.data.decode("utf-8"))["results"])
    # df = df.drop(
    #     ["vw", "n"],
    #     axis=1,
    # )
    df["timeindex"] = df["t"]

    df = df.rename(
        columns={
            "o": "open",
            "h": "high",
            "l": "low",
            "c": "close",
            "t": "timestamp",
            "v": "volume",
            "vw": "vwap",
            "n": "trades",
        }
    )

    df = df.set_index("timeindex")
    df.index = (
        pd.to_datetime(df.index, unit="ms", origin="unix")
        .tz_localize("UTC")
        .tz_convert("US/Eastern")
    )

    # Market hours only
    open_time, close_time = (
        pd.to_datetime("9:30:00").time(),
        pd.to_datetime("16:00:00").time(),
    )

    if not ext_hours:
        market_hours_mask = (df.index.time >= open_time) & (df.index.time < close_time)
        df = df[market_hours_mask]

    return df
