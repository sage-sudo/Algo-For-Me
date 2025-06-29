import asyncio
import threading
from MNDB.db_manager import DatabaseManager
from DATACOLLECTOR.kraken_ws_data import run_kraken_collector
from DASHUI.main_dashboard import build_dash_app
from datetime import datetime, timedelta, timezone
from DYNAMICS.dynamic_params import DB_PATH, START_AT_MINUTES
from DATACOLLECTOR.kraken_historical_data import fetch_kraken_ohlc

db = DatabaseManager(DB_PATH)

async def fetch_and_patch_gap(start_ts, end_ts, db):
    print("🔧 Patching data gap before WebSocket starts...")
    df = fetch_kraken_ohlc(start_ts, end_ts)
    for _, row in df.iterrows():
        db.save(dict(row))
    print(f"✅ Patched {len(df)} candles from REST API.")
    db.export_to_parquet("data/bootstrap.parquet")  # Optional bootstrapping export

async def main():
    end = datetime.now(tz=timezone.utc).replace(second=0, microsecond=0)
    start = end - timedelta(minutes=START_AT_MINUTES)
    await fetch_and_patch_gap(start, end, db)

    collector_task = asyncio.create_task(run_kraken_collector(db))

    def run_dash():
        app = build_dash_app()
        app.run(debug=False, use_reloader=False)

    dash_thread = threading.Thread(target=run_dash, daemon=True)
    dash_thread.start()

    await collector_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 User requested shutdown.")
