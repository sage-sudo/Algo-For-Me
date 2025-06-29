import asyncio, json, websockets, ssl
from datetime import datetime
from DYNAMICS.dynamic_params import ALL_INTERVAL, LIVE_PAIR, PARQUET_PATH

ssl_context = ssl._create_unverified_context()
KRAKEN_WS_V2_URL = "wss://ws.kraken.com/v2"

# Terminal colors and spinner frames
class TerminalColors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

spinner_frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

async def run_kraken_collector(db):
    current_candle_ts = None
    counter = 0
    latest_candle = None
    spinner_index = 0

    async def connect():
        nonlocal current_candle_ts, counter, latest_candle, spinner_index
        async with websockets.connect(KRAKEN_WS_V2_URL, ssl=ssl_context) as ws:
            await ws.send(json.dumps({
                "method": "subscribe",
                "params": {
                    "channel": "ohlc",
                    "symbol": [LIVE_PAIR],
                    "interval": ALL_INTERVAL
                }
            }))

            async for message in ws:
                try:
                    data = json.loads(message)

                    # Spinner to show activity
                    spinner_char = spinner_frames[spinner_index % len(spinner_frames)]
                    spinner_index += 1

                    if data.get("channel") != "ohlc" or "data" not in data:
                        # Print spinner to show live feed even on non-candle messages
                        print(f"\r{TerminalColors.CYAN}Live streaming {spinner_char}...{TerminalColors.RESET}", end='', flush=True)
                        continue

                    candles = data["data"]
                    if not isinstance(candles, list):
                        candles = [candles]

                    for candle in candles:
                        ts = datetime.fromisoformat(candle["interval_begin"].replace("Z", "+00:00"))

                        c = {
                            "timestamp": ts.isoformat(),
                            "open": float(candle["open"]),
                            "high": float(candle["high"]),
                            "low": float(candle["low"]),
                            "close": float(candle["close"]),
                            "volume": float(candle["volume"]),
                        }

                        # Sanity checks
                        if c["high"] == c["low"] or c["volume"] == 0:
                            continue
                        if not (c["low"] <= c["open"] <= c["high"] and c["low"] <= c["close"] <= c["high"]):
                            continue

                        # New candle finalized?
                        if current_candle_ts != ts:
                            if latest_candle:
                                db.save(latest_candle)
                                counter += 1

                                # Poetic candle printout
                                print(f"\n{TerminalColors.GREEN}{TerminalColors.BOLD}📡 Candle #{counter} Finalized — {latest_candle['timestamp']}{TerminalColors.RESET}")
                                print(f"{TerminalColors.YELLOW}O:{latest_candle['open']:.5f}  H:{latest_candle['high']:.5f}  L:{latest_candle['low']:.5f}  C:{latest_candle['close']:.5f}  V:{latest_candle['volume']:.2f}{TerminalColors.RESET}")
                                print(f"{TerminalColors.MAGENTA}✨ The market's pulse, a moment captured in time ✨{TerminalColors.RESET}")

                                if counter % 1 == 0:
                                    db.export_to_parquet(PARQUET_PATH)
                                    print(f"{TerminalColors.CYAN}💽 Exported to Parquet @ {latest_candle['timestamp']}{TerminalColors.RESET}")

                            current_candle_ts = ts

                        # Always update latest candle
                        latest_candle = c

                    # Show live streaming spinner after candles processed
                    print(f"\r{TerminalColors.CYAN}Live streaming {spinner_char}...{TerminalColors.RESET}", end='', flush=True)

                except Exception as e:
                    print(f"\n{TerminalColors.RED}❌ Parse fail: {e}{TerminalColors.RESET}")

    while True:
        try:
            await connect()
        except Exception as e:
            print(f"\n{TerminalColors.RED}⚠️ WS error: {e}, reconnecting in 5s...{TerminalColors.RESET}")
            await asyncio.sleep(5)
