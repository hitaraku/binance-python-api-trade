import configparser
import json
from binance.client import Client 
import time
import re

from datetime import datetime

from binance.enums import *
from binance.exceptions import *

# load config
inifile = configparser.ConfigParser()
inifile.read('../config/config.ini', 'UTF-8')
 
# get APIKEY
api_key = inifile.get('settings', 'API_KEY')
api_secret = inifile.get('settings', 'API_SECRET')

# set binance client APIKEY
client = Client(api_key, api_secret)

# get all symbol prices
prices = client.get_all_tickers()

while 1:
    # 自分のBTCを取得
    balance = client.get_asset_balance(asset='BTC')
    # Freeは「現在使用できるBTC」
    print("free myBTC : " + str(balance['free']))
    # すべての価格を取得
    prices = client.get_all_tickers()
    # 取得した価格を表示
    print(prices)
    # 7秒待ち
    time.sleep(7)


