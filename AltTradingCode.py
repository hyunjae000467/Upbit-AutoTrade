import pyupbit
import matplotlib.pyplot as plt
import requests
import datetime
import sys
import time

# Discord 웹훅 URL
WEBHOOK_URL = "https://discord.com/api/webhooks/954074224732033044/PNJM8t_MFR8JX7LkkRvpKjNHPGaKNSf7GgJDC3SzDK67xbLSezDYY9x9Nyn3Ykcbh5mz"

# 매수 매도 조건
MACD_THRESHOLD = 0
RSI_THRESHOLD = 30

# 매수/매도
while True:
    # 현재 가격을 가져옵니다.
    current_price = upbit.get_current_price("KRW-BTC")

    # 잔고를 가져옵니다.
    balance = upbit.get_balance("KRW")

    # RSI를 가져옵니다.
    current_rsi = upbit.get_rsi("KRW-BTC", 14)

    # MACD를 가져옵니다.
    current_macd = pyupbit.get_macd("KRW-BTC", 12, 26, 9)

    # 그래프를 그립니다.
    plt.plot(current_price, label="Price")
    plt.plot(current_rsi, label="RSI")
    plt.plot(current_macd, label="MACD")

    # 매수
    if current_macd[-1] > current_macd[-2] and current_rsi < RSI_THRESHOLD:
        try:
            order = pyupbit.buy("KRW-BTC", balance / current_price, "market")
            msg = "[TRANSACTION] 매수, 매수 이유: MACD 골든크로스, RSI 30 미만 " + str(datetime.datetime.now())
            requests.post(WEBHOOK_URL, data={"content": msg})
        except Exception as e:
            msg = "[ERROR] 매수 실패, 에러 메시지: " + str(e)
            requests.post(WEBHOOK_URL, data={"content": msg})

    # 매도
    if current_macd[-1] < current_macd[-2] and current_rsi > RSI_THRESHOLD:
        try:
            order = pyupbit.sell("KRW-BTC", balance / current_price, "market")
            msg = "[TRANSACTION] 매도, 매도 이유: MACD 데드크로스, RSI 70 이상 " + str(datetime.datetime.now())
            requests.post(WEBHOOK_URL, data={"content": msg})
        except Exception as e:
            msg = "[ERROR] 매도 실패, 에러 메시지: " + str(e)
            requests.post(WEBHOOK_URL, data={"content": msg})

    # 그래프에 매수/매도 시점을 표시합니다.
    plt.plot([buy_time, sell_time], [buy_price, sell_price], "ro")

    # 그래프를 이미지 파일로 저장합니다.
    plt.savefig("graph.png")

    # Discord 웹훅에 이미지 파일 전송
    files = {"file": open("graph.png", "rb")}
    requests.post(WEBHOOK_URL, files=files)

    # Discord 웹훅에 메시지 전송
    for line in sys.stdout:
        requests.post(WEBHOOK_URL, data={"content": line + "\n"})

    time.sleep(1)
