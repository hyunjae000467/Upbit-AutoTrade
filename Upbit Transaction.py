#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import talib
import pyupbit
import time
import requests
import matplotlib.pyplot as plt

# Define MACD and RSI parameters
fast_period = 12
slow_period = 26
signal_period = 9
rsi_period = 14

# Discord webhook URL
webhook_url = "REDACTED FOR SECURITY REASON"

buy_points = []  # List to track buy signal indices
sell_points = []  # List to track sell signal indices


def login_to_upbit(access_key, secret_key):
    upbit = pyupbit.Upbit(access_key, secret_key)
    print("[INFO] Successfully logged in to Upbit API")
    send_to_discord(webhook_url, [], "[INFO] Successfully logged in to Upbit API")
    return upbit


def check_buy_signal(ticker, curr_price):
    # Fetch historical data
    df = pyupbit.get_ohlcv(ticker=ticker, interval='minute3', count=3360)
    close_prices = df['close']

    # Calculate MACD and signal line
    macd, signal, _ = talib.MACD(close_prices, fastperiod=fast_period, slowperiod=slow_period, signalperiod=signal_period)

    # Calculate RSI
    rsi = talib.RSI(close_prices, timeperiod=rsi_period)

    # Check if MACD line crosses signal line from below and RSI is below 30
    if macd[-1] > signal[-1] and macd[-2] < signal[-2] and rsi[-1] < 30:
        buy_signal_message = f"[WARNING] Buy signal triggered: MACD: {macd[-1]}, Signal: {signal[-1]}, RSI: {rsi[-1]}"
        print("[INFO] Checking Buy Signal...")
        send_to_discord(webhook_url, [], "[INFO] Checking Buy Signal...")
        print(f"[INFO] Reason for Buy Signal: MACD: {macd[-1]} > Signal: {signal[-1]} and RSI: {rsi[-1]} < 30")
        send_to_discord(webhook_url, [], f"[INFO] Reason for Buy Signal: MACD: {macd[-1]} > Signal: {signal[-1]} and RSI: {rsi[-1]} < 30")
        send_to_discord(webhook_url, [], buy_signal_message)
        buy_points.append(len(macd) - 1)  # Add the index of the buy signal
        return True
    else:
        print("[INFO] Checking Buy Signal...")
        send_to_discord(webhook_url, [], "[INFO] Checking Buy Signal...")
        print(f"[INFO] Reason for Not Sending Buy Signal: MACD: {macd[-1]} <= Signal: {signal[-1]} or RSI: {rsi[-1]} >= 30")
        send_to_discord(webhook_url, [], f"[INFO] Reason for Not Sending Buy Signal: MACD: {macd[-1]} <= Signal: {signal[-1]} or RSI: {rsi[-1]} >= 30")
        return False


def check_sell_signal(ticker, curr_price, buy_price):
    # Fetch historical data
    df = pyupbit.get_ohlcv(ticker=ticker, interval='minute3', count=3360)
    close_prices = df['close']

    # Calculate MACD and signal line
    macd, signal, _ = talib.MACD(close_prices, fastperiod=fast_period, slowperiod=slow_period, signalperiod=signal_period)

    # Check if MACD line crosses signal line from above
    if macd[-1] < signal[-1] and macd[-2] > signal[-2]:
        sell_signal_message = f"[WARNING] Sell signal triggered: MACD: {macd[-1]}, Signal: {signal[-1]}"
        print("[INFO] Checking Sell Signal...")
        send_to_discord(webhook_url, [], "[INFO] Checking Sell Signal...")
        print(f"[INFO] Reason for Sell Signal: MACD: {macd[-1]} < Signal: {signal[-1]}")
        send_to_discord(webhook_url, [], f"[INFO] Reason for Sell Signal: MACD: {macd[-1]} < Signal: {signal[-1]}")
        send_to_discord(webhook_url, [], sell_signal_message)
        sell_points.append(len(macd) - 1)  # Add the index of the sell signal
        return True
    else:
        print("[INFO] Checking Sell Signal...")
        send_to_discord(webhook_url, [], "[INFO] Checking Sell Signal...")
        print(f"[INFO] Reason for Not Sending Sell Signal: MACD: {macd[-1]} >= Signal: {signal[-1]}")
        send_to_discord(webhook_url, [], f"[INFO] Reason for Not Sending Sell Signal: MACD: {macd[-1]} >= Signal: {signal[-1]}")
        return False


def send_to_discord(webhook_url, image_paths=None, message=""):
    if image_paths is None:
        image_paths = []
    payload = {
        "content": message
    }
    files = []
    for image_path in image_paths:
        files.append(("file", open(image_path, "rb")))
    response = requests.post(webhook_url, data=payload, files=files)
    if response.status_code != 204:
        print("[ERROR] Failed to send message to Discord")
        send_to_discord(webhook_url, [], "[ERROR] Failed to send message to Discord")


def main():
    access_key = "REDACTED FOR SECURITY REASON"
    secret_key = "REDACTED FOR SECURITY REASON"
    upbit = login_to_upbit(access_key, secret_key)
    ticker = "KRW-BTC"
    buy_price = None
    while True:
        curr_price = pyupbit.get_current_price(ticker)
        if curr_price is None:
            continue

        if check_buy_signal(ticker, curr_price):
            # Place a buy order
            balance = upbit.get_balance(ticker.split('-')[1])
            buy_amount = balance * 0.8 * 0.995  # 80% of the current balance
            buy_order = upbit.buy_market_order(ticker, buy_amount)
            buy_price = buy_amount
            print("[INFO] Buy order placed:", buy_order)
            send_to_discord(webhook_url, [], "[INFO] Buy order placed:\n" + str(buy_order))

        if check_sell_signal(ticker, curr_price, buy_price):
            # Place a sell order
            balance = upbit.get_balance(ticker.split('-')[0])
            sell_amount = balance * 0.8  # 80% of the current balance
            sell_order = upbit.sell_market_order(ticker, sell_amount)
            print("[INFO] Sell order placed:", sell_order)
            send_to_discord(webhook_url, [], "[INFO] Sell order placed:\n" + str(sell_order))

        time.sleep(10)  # Sleep for 10 seconds



if __name__ == "__main__":
    main()


# In[ ]:




