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

# シンボルの数を取得
prices = client.get_all_tickers()
symbolVol = len(prices)

# すべてのsymbol情報を取得
volumes = client.get_ticker()

# symbolの数だけsymbolとvolumeを表示する
for i in range(symbolVol):
    print("symbol: " , volumes[i]['symbol'], "volume: ", volumes[i]['volume'])


