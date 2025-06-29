HISTORICAL_PAIR = "BTC/USD" #"XXBTZUSD"
LIVE_PAIR = "BTC/USD"

MIN = {'one_min':1, 'five_min':5, 'fifteen_min':15, 'thirty_min':30, 
      'one_hour':60, 'four_hours':240, 'one_day':1440, 'one_week':10080, 'two_weeks':21600}

TIME_FRAME = ['one_min', 'five_min', 'fifteen_min', 'thirty_min', 'one_hour'
              'four_hours', 'one_day', 'one_week', 'two_weeks']

NUMBER = 1

HOW_MANY_CANDLES = 666    #1080000

START_AT_MINUTES = MIN.get(TIME_FRAME[NUMBER]) * HOW_MANY_CANDLES

ALL_INTERVAL = MIN.get(TIME_FRAME[NUMBER]) # in minutes

POST = f"test1_{START_AT_MINUTES}"
DB_PATH = f"data/crypto_{ALL_INTERVAL}_min_{POST}.sqlite"
PARQUET_PATH = f"data/ohlc_{ALL_INTERVAL}_min_{POST}.parquet"
