import requests

TRC20_FEE = 1.0  # USDT комиссия (TRC20)
MIN_PROFIT_THRESHOLD = 0.2  # %

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
    except Exception as e:
        print("Binance error:", e)
        return []

def get_okx_usdt_kgz():
    url = "https://www.okx.com/v3/c2c/otc-ticker?quoteCurrency=KGS&baseCurrency=USDT&side=sell&paymentMethod=&userType=all"
    try:
        r = requests.get(url)
        data = r.json()
        return [float(d["price"]) for d in data.get("data", [])[:5]]
    except Exception as e:
        print("OKX error:", e)
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
    except Exception as e:
        print("Bybit error:", e)
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
                    profit_usdt = (sell_price - buy_price) - TRC20_FEE
                    percent = (profit_usdt / buy_price) * 100
                    if percent >= MIN_PROFIT_THRESHOLD:
                        results.append({
                            "pair": f"{source} → {target}",
                            "buy": buy_price,
                            "sell": sell_price,
                            "profit_percent": round(percent, 2),
                            "p100": round((profit_usdt / buy_price) * 100, 2),
                            "p500": round((profit_usdt / buy_price) * 500, 2),
                            "p1000": round((profit_usdt / buy_price) * 1000, 2)
                        })

    if not results:
        return ["😕 No profitable routes found."]

    results.sort(key=lambda x: x["profit_percent"], reverse=True)
    return [
        f"🔄 {r['pair']}\n"
        f"🔻 Buy: {r['buy']:.2f} USDT\n"
        f"🔺 Sell: {r['sell']:.2f} USDT\n"
        f"💰 Profit: {r['profit_percent']:.2f}%\n"
        f"📊 At $100: +{r['p100']} USDT | $500: +{r['p500']} | $1000: +{r['p1000']}\n"
        for r in results[:5]
    ]
