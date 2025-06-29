# ================= mndb/database_manager.py =================
import sqlite3, os
import pandas as pd
from threading import Lock

class DatabaseManager:
    def __init__(self, db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.lock = Lock()
        self._create_table()

    def _create_table(self):
        with self.lock:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS candles (
                    timestamp TEXT PRIMARY KEY,
                    open REAL, high REAL, low REAL, close REAL, volume REAL
                )
            """)
            self.conn.commit()

    def insert_candle(self, candle):
        with self.lock:
            self.conn.execute("""
                INSERT OR REPLACE INTO candles (timestamp, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (candle["timestamp"], candle["open"], candle["high"], candle["low"], candle["close"], candle["volume"]))
            self.conn.commit()

    def save(self, candle):
        self.insert_candle(candle)

    def export_to_parquet(self, pq_path):
        with self.lock:
            df = pd.read_sql("SELECT * FROM candles ORDER BY timestamp", self.conn, parse_dates=["timestamp"])
            df.to_parquet(pq_path, index=False)

    def close(self):
        self.conn.close()