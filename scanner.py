
import requests

TRC20_FEE = 1.0
MIN_PROFIT_THRESHOLD = 0.5

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
    try:
        r = requests.post(url, json=payload, headers=headers)
        offers = r.json().get("data", [])
        return [float(o["adv"]["price"]) for o in offers if o.get("adv")]
    except:
        return []

def get_okx_usdt_kgz():
    url = "https://www.okx.com/v3/c2c/otc-ticker?quoteCurrency=KGS&baseCurrency=USDT&side=sell&paymentMethod=&userType=all"
    try:
        r = requests.get(url)
        data = r.json()
        return [float(d["price"]) for d in data.get("data", [])[:5]]
    except:
        return []

def get_bybit_usdt_kgz():
    url = "https://api2.bybit.com/fiat/otc/item/online"
    payload = {
        "userId": "",
        "tokenId": "USDT",
        "currencyId": "KGS",
        "payment": [],
        "side": "1",
        "size": "5",
        "page": "1"
    }
    try:
        r = requests.post(url, json=payload)
        data = r.json()
        return [float(d["price"]) for d in data.get("result", {}).get("items", [])]
    except:
        return []

def compare_all_exchanges():
    prices = {
        "Binance": get_binance_usdt_kgz(),
        "OKX": get_okx_usdt_kgz(),
        "Bybit": get_bybit_usdt_kgz()
    }

    results = []
    for source in prices:
        for target in prices:
            if source == target:
                continue
            for buy_price in prices[source]:
                for sell_price in prices[target]:
                    profit = sell_price - buy_price - TRC20_FEE
                    percent = (profit / buy_price) * 100
                    if percent >= MIN_PROFIT_THRESHOLD:
                        results.append({
                            "pair": f"{source} → {target}",
                            "buy": buy_price,
                            "sell": sell_price,
                            "profit": percent
                        })

    if not results:
        return ["😕 Выгодных связок не найдено."]

    results.sort(key=lambda x: x["profit"], reverse=True)
    return [
        f"🔄 {r['pair']}\n🔻 Купить: {r['buy']} KGS\n🔺 Продать: {r['sell']} KGS\n💰 Чистая прибыль: {r['profit']:.2f}%\n"
        for r in results[:5]
    ]
