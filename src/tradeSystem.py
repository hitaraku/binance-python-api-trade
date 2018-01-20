import configparser
import json
from binance.client import Client 
import time
import re
import math

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

print(prices[0]['symbol'])

# before, after prices
beforePrices = [prices[i]['price'] for i in range(symbolLen)]
afterPrices = [0 for i in range(symbolLen)]

# log to file
file_object  = open("../log/" + datetime.now().strftime("%Y%m%d_%H%M%S")+"_log.txt", "w+") 

def buyCoin( symbol, afterPrice, tickerCount ):
    try:
        print("called buy")
        balance = client.get_asset_balance(asset='BTC')
        orderQuantity = round(float(balance['free']) / (float(afterPrice) * 1.01))
        print(orderQuantity)
        print(afterPrice)

        order = client.order_limit_buy(
                symbol=symbol,
                price=afterPrice,
                quantity=orderQuantity)

        """ [TEST]
        order = client.order_limit_buy(
            symbol="TRXBTC",
            price='0.00000995',
            quantity='2000')



            order = client.create_test_order(
            symbol=symbol,
            side=SIDE_BUY,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            price=afterPrice,
            quantity=orderQuantity)
        """ 

        count = 0
        while 1:
            time.sleep(1)
            checkOrder = client.get_order(
                symbol=symbol,
                orderId=order['orderId'])
            print(checkOrder['status'])
            if str(checkOrder['status']) == "FILLED":
                break
            if str(checkOrder['status']) == "NEW":
                count = 1 + count
            if count > 10:
                # cancel order
                result = client.cancel_order(
                    symbol=symbol,
                    orderId=checkOrder['orderId'])
                print(result)
                return

        # bougut complete
        print("bought")
        time.sleep(10)
        print("bought end")
        checkOrder = client.get_order(
            symbol=symbol,
            orderId=order['orderId'])
        sellCoin( symbol, tickerCount, checkOrder['origQty'] )
        print("sell end")
        return

    except BinanceAPIException as e:
        print(e.status_code)
        print(e.message)
        return



def sellCoin( symbol, tickerCount, orderQuantity ): 
    try:
        print("called sell")
        prices = client.get_all_tickers()
        print(prices[tickerCount]['price'])
        print("orderQuantity: " + orderQuantity)

        floatSymbolValue = float(client.get_symbol_info(symbol=symbol)['filters'][1]['minQty'])
        print(floatSymbolValue)

        count = 0
        while 1:
            qtyCount = floatSymbolValue * math.pow(10, count)
            if qtyCount >= 1.0:
                break
            count += 1
        
        # This code trim "BTC" string from symbol
        balance = client.get_asset_balance(asset=symbol.replace("BTC", ""))

        # calucrate quantity from ticker quantity
        amount = float(balance['free'])
        precision = count
        amt_str = "{:0.0{}f}".format(amount, precision)
        print(float(amt_str))

        # client.get_symbol_info(symbol=symbol)['filters'][1]['minQty']

        sellOrder = client.order_limit_sell(
            symbol=symbol,
            price=prices[tickerCount]['price'],
            quantity=float(amt_str))

        """ [TEST]
        order = client.create_test_order(
            symbol=symbol,
            side=SIDE_SELL,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            price=prices[tickerCount]['price'],
            quantity=orderQuantity)

        """

        while 1:
            time.sleep(1)
            checkOrder = client.get_order(
                symbol=symbol,
                orderId=sellOrder['orderId'])
            print(checkOrder['status'])
            if str(checkOrder['status']) == "FILLED":
                break
        print("sold")
        return

    except BinanceAPIException as e:
        print(e.status_code)
        print(e.message)
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
    for i in range(symbolLen):
        # 7秒後の現在の価格を取得
        afterPrices[i] = prices[i]['price']
        # 前回の価格と現在の価格を比較し、パーセンテージを計算
        pricePropotion = 100 - (float(afterPrices[i]) / float(beforePrices[i])) * 100
        # BTCのそれぞれの銘柄で指定パーセンテージ下がったら買いを入れる。5%以上下がったら買いを入れる。
        if ( pricePropotion ) > 5.0: 
            # Ticker BTC
            if re.search(r'BTC', prices[i]['symbol']) and (round (float(balance['free']) / (float(afterPrices[i]) * 1.03)) ) > 0.0:
                # write file
                file_object.write('time: ' + datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ' , ticker: ' + prices[i]['symbol'] + ' , PricePropotion: ' + str(pricePropotion) + ' , afterprice: ' + afterPrices[i] + ' , beforePrice: ' + beforePrices[i] + "\n")
                # 買いを入れたときの情報を表示
                print('time: ' + datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ' , ticker: ' + prices[i]['symbol'] + ' , PricePropotion: ' + str(pricePropotion) + ' , afterprice: ' + afterPrices[i] + ' , beforePrice: ' + beforePrices[i])
                # 買いを入れるときにTickerの「シンボル」、「現在の価格」、「ループの番号」をbuyCoin関数に渡す
                buyCoin(prices[i]['symbol'], afterPrices[i], i)
                break

    for i in range(symbolLen):
        beforePrices[i] = prices[i]['price']

file_object.close()


