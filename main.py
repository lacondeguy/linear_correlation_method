import websocket
import json
import numpy as np
from sklearn import linear_model


BTC_data = []
ETH_data = []
changes_data = []
max_change = 0.0
delay = 1000  # 100, 250, 500, 1000 (ms)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("Close connection")

def on_open(ws):
    print("Connected")

def correlation(btc_array, eth_array):
    x = np.array(btc_array).reshape((-1, 1))
    y = np.array(eth_array)
    model = linear_model.LinearRegression()
    model.fit(x, y)
    prices = model.predict(x)
    changes = y - prices
    return changes, prices

def on_message(ws, message):
    result = json.loads(message)
    global max_change

    try:
        if result.get('s') == 'BTCUSDT':
            btc_price = result.get('b')[0][0]
            BTC_data.append(float(btc_price))
        if result.get('s') == 'ETHUSDT':
            eth_price = result.get('b')[0][0]
            ETH_data.append(float(eth_price))

        changes, prices = correlation(BTC_data, ETH_data)
        change_current = abs(changes[0] / prices[0]) * 100
        changes_data.append(change_current)
        slice_value = int(-3600*(1000/delay))
        changes_data_per_hour = changes_data[-3:]
        max_changes_per_hour = float(max(changes_data_per_hour))

        if max_change != max_changes_per_hour and max_changes_per_hour > 0.02:
            max_change = max_changes_per_hour
            print(f'Price of ETHUSDT has changed by {max_change:.4f}% in the last 60 minutes.')

    except:
        ...

def main():
    while 1:
        ws = websocket.WebSocketApp(f'wss://stream.binance.com:9443/ws/btcusdt@depth@{delay}ms/ethusdt@depth@{delay}ms',
                                  on_message = on_message,
                                  on_error = on_error,
                                  on_close = on_close)
        ws.on_open = on_open
        ws.run_forever()


if __name__ == '__main__':
    main()

