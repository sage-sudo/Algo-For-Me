import pandas as pd
import requests
from DYNAMICS.dynamic_params import ALL_INTERVAL, HISTORICAL_PAIR
from datetime import datetime, timezone

def fetch_kraken_ohlc(start_ts, end_ts):
    url = "https://api.kraken.com/0/public/OHLC"
    since = int(start_ts.timestamp())
    all_candles = []

    while since < int(end_ts.timestamp()):
        try:
            response = requests.get(url, params={
                "pair": HISTORICAL_PAIR,
                "interval": ALL_INTERVAL,
                "since": since
            }, timeout=10, verify=False)

            data = response.json()
            if "error" in data and data["error"]:
                print(f"🚫 Kraken error: {data['error']}")
                break

            ohlc = data["result"].get(HISTORICAL_PAIR, [])
            for candle in ohlc:
                ts = datetime.fromtimestamp(candle[0], tz=timezone.utc)
                if ts >= end_ts:
                    break
                all_candles.append({
                    "timestamp": ts.isoformat(),
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": float(candle[6])
                })

            since = ohlc[-1][0] + ALL_INTERVAL * 60 if ohlc else since + ALL_INTERVAL * 60

        except Exception as e:
            print(f"❌ REST fetch fail: {e}")
            break

    return pd.DataFrame(all_candles)
