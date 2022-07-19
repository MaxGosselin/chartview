from concurrent.futures import process
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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
    interday = True if timespan != "minute" else False
    target_aggs = api_client.get_aggs(
        ticker,
        multiplier,
        timespan,
        from_,
        to,
        adjusted=True,
        limit=500000,
        raw=True,
    )
    daily_start = (datetime.strptime(from_, "%Y-%m-%d") - timedelta(days=201)).strftime(
        "%Y-%m-%d"
    )
    timestr = str(multiplier) + " " + timespan
    daily_aggs = api_client.get_aggs(
        ticker,
        1,
        "day",
        daily_start,
        to,
        adjusted=True,
        limit=500000,
        raw=True,
    )

    if target_aggs.status < 400:
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
        aggs_df = adjust_timeframe(target_aggs, ext_hours, interday)
        data_df = adjust_timeframe(daily_aggs, ext_hours, True)
        # print(processed[:5], type(processed[0]))

        aggs_df = calculate_stuff(aggs_df, data_df, timestr)
        # print(aggs_df)
        return aggs_df.to_dict("records"), target_aggs.status
    else:
        # TODO: Handle errs cogently
        print(f"Error with ticker {ticker}")
        print(target_aggs.status, dir(target_aggs))
        return target_aggs.message, target_aggs.status


def calculate_stuff(df, daily, timestr):
    def weighted_vwap(grp):
        def compute_from_window(wdow):
            wv = df.loc[wdow.index]
            # print(wv[["vwap", "volume"]])
            avg = np.average(wv["vwap"], weights=wv["volume"])
            # print(avg)
            return avg

        if len(df):
            grp["true_vwap"] = (
                grp["vwap"]
                .rolling(window=len(df), min_periods=1)
                .apply(compute_from_window)
            )
        # print(df)
        # print(type(grp), grp)
        return grp

    def resample_daily_close(df, daily, timestr):

        daily["ma10"] = daily["close"].rolling(10, min_periods=1).mean()
        daily["ma20"] = daily["close"].rolling(20, min_periods=1).mean()
        daily["ma100"] = daily["close"].rolling(100, min_periods=1).mean()
        daily["ma200"] = daily["close"].rolling(200, min_periods=1).mean()
        daily["ema10"] = (
            daily["close"]
            .ewm(span=10, min_periods=0, adjust=False, ignore_na=False)
            .mean()
        )
        daily["ema20"] = (
            daily["close"]
            .ewm(span=20, min_periods=0, adjust=False, ignore_na=False)
            .mean()
        )
        daily["ema65"] = (
            daily["close"]
            .ewm(span=65, min_periods=0, adjust=False, ignore_na=False)
            .mean()
        )
        print(daily.loc[:, "ma10":"ema65"])
        codec = {"minute": "T", "day": "D", "week": "W", "month": "M"}
        timestr = timestr.split()
        timestr = timestr[0] + codec[timestr[1]]

        df["ma10"] = daily["ma10"].resample(timestr).interpolate(method="linear")
        df["ma10"] = df["ma10"].ffill()
        df["ma20"] = daily["ma20"].resample(timestr).interpolate(method="linear")
        df["ma20"] = df["ma20"].ffill()
        df["ma100"] = daily["ma100"].resample(timestr).interpolate(method="linear")
        df["ma100"] = df["ma100"].ffill()
        df["ma200"] = daily["ma200"].resample(timestr).interpolate(method="linear")
        df["ma200"] = df["ma200"].ffill()
        df["ema10"] = daily["ema10"].resample(timestr).interpolate(method="linear")
        df["ema10"] = df["ema10"].ffill()
        df["ema20"] = daily["ema20"].resample(timestr).interpolate(method="linear")
        df["ema20"] = df["ema20"].ffill()
        df["ema65"] = daily["ema65"].resample(timestr).interpolate(method="linear")
        df["ema65"] = df["ema65"].ffill()

        return df

    df["true_vwap"] = df.groupby(df.index.floor("d"))[["vwap", "volume"]].apply(
        weighted_vwap
    )["true_vwap"]
    # print(x["true_vwap"])
    #  = x
    df["bar_range"] = ((df.high / df.low) - 1) * 100
    # print(df.head(10))

    df["adr"], df["atr"] = get_ATR_ADR(df)
    # df = resample_daily_close(df, daily, timestr)
    # print(df.loc[:, "ma10":"ema65"])
    print(df.head(10))
    return df


def adjust_timeframe(rawdata: list, ext_hours, interday):
    """Convert API data to pd DataFrame and set index on timestamp."""

    df = pd.DataFrame(json.loads(rawdata.data.decode("utf-8"))["results"])
    try:
        df = df.drop(
            ["a", "op"],
            axis=1,
        )
    except:
        print(f"Tried dropping 'a', 'op', but columns are: {df.columns.values}")

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

    if not ext_hours and not interday:
        market_hours_mask = (df.index.time >= open_time) & (df.index.time < close_time)
        df = df[market_hours_mask]

    return df


def get_ATR_ADR(data_df):
    """ADR and ATR computation"""

    range_df = data_df
    # print(range_df)
    high_low = range_df["high"] - range_df["low"]  # / range_df["close"]
    high_low_adr = range_df["high"] / range_df["low"]

    adr = (high_low_adr.rolling(20).sum() / 20) - 1

    high_close = np.abs(
        range_df["high"] - range_df["close"].shift()
    )  # / range_df["close"]
    low_close = np.abs(
        range_df["low"] - range_df["close"].shift()
    )  # / range_df["close"]

    ranges = pd.concat([high_low, high_close, low_close], axis=1)

    true_range = np.max(ranges, axis=1)
    atr = true_range.rolling(14).sum() / 14
    # atr_3 = true_range.rolling(3).sum() / 3
    # atr_20 = true_range.rolling(20).sum() / 20
    # atr_3_20 = atr_3[-1] / atr_20[-1]
    adr, atr = adr.fillna(0), atr.fillna(0)
    print(adr, atr)
    return adr, atr
