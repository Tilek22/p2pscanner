
import requests

# Настройки комиссий (в USDT)
TRC20_FEE = 1.0  # Вывод между биржами
MIN_PROFIT_THRESHOLD = 0.5  # Минимальная прибыль в %

def get_binance_usdt_kgz():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    payload = {
        "page": 1,
        "rows": 5,
        "payTypes": [],
        "asset": "USDT",
        "tradeType": "SELL",
        "fiat": "KGS"
    }
    headers = {"Content-Type": "application/json"}
    r = requests.post(url, json=payload, headers=headers)
    data = r.json()
    offers = data.get("data", [])
    return [float(o["adv"]["price"]) for o in offers if o.get("adv")]

def get_okx_usdt_kgz():
    url = "https://www.okx.com/v3/c2c/otc-ticker?quoteCurrency=KGS&baseCurrency=USDT&side=sell&paymentMethod=&userType=all"
    try:
        r = requests.get(url)
        data = r.json()
        return [float(d["price"]) for d in data.get("data", [])[:5]]
    except:
        return []

def compare_binance_okx():
    binance_prices = get_binance_usdt_kgz()
    okx_prices = get_okx_usdt_kgz()
    if not binance_prices or not okx_prices:
        return ["❌ Не удалось получить данные с бирж"]

    results = []
    for buy_price in binance_prices:
        for sell_price in okx_prices:
            profit = sell_price - buy_price - TRC20_FEE
            percent = (profit / buy_price) * 100
            if percent >= MIN_PROFIT_THRESHOLD:
                results.append(f"🔄 Купить на Binance за {buy_price} KGS → продать на OKX за {sell_price} KGS\n💰 Прибыль: {percent:.2f}%\n")

    if not results:
        return ["😕 Подходящих связок с прибылью выше 0.5% не найдено"]
    return results
