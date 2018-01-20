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
symbolLen = len(prices)

# before, after prices
beforePrices = [prices[i]['price'] for i in range(symbolLen)]
afterPrices = [0 for i in range(symbolLen)]

def buyCoin( symbol, afterPrice, tickerCount ):
    print("called buy")

    order = client.create_test_order(
        symbol=symbol,
        side=SIDE_BUY,
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        price=100,
        quantity=10)

    print(order)

    return

while 1:
    # 自分のBTCを取得
    balance = client.get_asset_balance(asset='BTC')
    # Freeは「現在使用できるBTC」
    print("free myBTC : " + str(balance['free']))
    # 7秒待ち
    time.sleep(7)
    # すべての価格を取得
    prices = client.get_all_tickers()
    # 取得した価格を表示
    # print(prices)
    for i in range(symbolLen):
        # 7秒後の現在の価格を取得
        afterPrices[i] = prices[i]['price']
        # 前回の価格と現在の価格を比較し、パーセンテージを計算
        pricePropotion = 100 - (float(afterPrices[i]) / float(beforePrices[i])) * 100
        # BTCのそれぞれの銘柄で指定パーセンテージ下がったら買いを入れる。今回はテストの為0パーセントで買いを入れる。
        if ( pricePropotion ) > 0.0: 
            # Ticker BTC
            if re.search(r'BTC', prices[i]['symbol']) and (round (float(balance['free']) / (float(afterPrices[i]) * 1.03)) ) > 0.0:
                # 買いを入れたときの情報を表示
                print('time: ' + datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ' , ticker: ' + prices[i]['symbol'] + ' , PricePropotion: ' + str(pricePropotion) + ' , afterprice: ' + afterPrices[i] + ' , beforePrice: ' + beforePrices[i])
                # 買いを入れるときにTickerの「シンボル」、「現在の価格」、「ループの番号」をbuyCoin関数に渡す
                buyCoin(prices[i]['symbol'], afterPrices[i], i)
                break

    for i in range(symbolLen):
        beforePrices[i] = prices[i]['price']
