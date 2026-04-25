import pandas as pd
import requests
import ta
import os
import json
from telegram import Bot

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    res = requests.post(url, data=data)
    print(res.text)
bot = Bot(token=TOKEN)

STOCKS = [
"ENGRO","OGDC","HBL","PSO","UBL","MCB","LUCK","FFC","POL","SNGP",
"SYS","TRG","PIOC","DGKC","BAHL","EFERT","HUBC","NML","NBP","KEL"
]

def get_data(symbol):
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}.KAR?apikey=demo"
    res = requests.get(url).json()
    data = res.get("historical", [])
    df = pd.DataFrame(data)

    if df.empty:
        return None

    df = df.rename(columns={"close": "Close"})
    df = df.sort_values("date")
    return df

def analyze(stock):
    df = get_data(stock)
    if df is None or len(df) < 30:
        return None

    df['MA5'] = df['Close'].rolling(5).mean()
    df['MA20'] = df['Close'].rolling(20).mean()
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()

    last = df.iloc[-1]
    prev = df.iloc[-2]

    score = 0

    if last['MA5'] > last['MA20']:
        score += 2
    else:
        score -= 2

    if 30 < last['RSI'] < 40:
        score += 2
    elif last['RSI'] > 65:
        score -= 2

    if last['Close'] > prev['Close']:
        score += 1
    else:
        score -= 1

    confidence = min(max((score + 5) * 10, 0), 100)

    if score >= 2:
        signal = "BUY"
    elif score <= -2:
        signal = "SELL"
    else:
        signal = "HOLD"

    return {
        "stock": stock,
        "signal": signal,
        "score": score,
        "confidence": confidence,
        "price": round(last['Close'],2),
        "RSI": round(last['RSI'],2)
    }

def load_portfolio():
    with open("portfolio.json") as f:
        return json.load(f)

def analyze_portfolio(portfolio):
    results = []
    total_profit = 0

    for stock, info in portfolio.items():
        buy_price = info["price"]
        qty = info["qty"]

        df = get_data(stock)
        if df is None:
            continue

        current_price = df.iloc[-1]['Close']

        profit = (current_price - buy_price) * qty
        percent = ((current_price - buy_price) / buy_price) * 100

        total_profit += profit

        stop_loss = buy_price * 0.95

        action = "HOLD"

        if current_price < stop_loss:
            action = "SELL (Stop-Loss)"
        elif percent > 5:
            action = "SELL (Profit)"

        results.append(
            f"{stock} | Qty:{qty} | Buy:{buy_price} | Now:{round(current_price,2)} | {round(percent,2)}% | Profit:{round(profit,2)} | SL:{round(stop_loss,2)} → {action}"
        )

    results.append(f"\n💰 TOTAL PROFIT: {round(total_profit,2)} PKR")

    return results

def run_bot():
    results = []

    for stock in STOCKS:
        try:
            r = analyze(stock)
            if r:
                results.append(r)
        except:
            continue

    results = sorted(results, key=lambda x: x['score'], reverse=True)

    top_buy = [r for r in results if r['signal']=="BUY"][:5]
    top_sell = [r for r in results if r['signal']=="SELL"][:5]

    portfolio = load_portfolio()
    portfolio_report = analyze_portfolio(portfolio)

    message = "📊 PSX FINAL REPORT\n\n"
    
   message += "🟢 TOP BUY:\n"
for r in top_buy:
    message += f"{r['stock']} | Price:{r['price']} | Score:{r['score']} | Conf:{r['confidence']}%\n"

message += "\n🔴 TOP SELL:\n"
for r in top_sell:
    message += f"{r['stock']} | Price:{r['price']} | Score:{r['score']} | Conf:{r['confidence']}%\n"

    message += "\n💼 YOUR PORTFOLIO:\n"
    for p in portfolio_report:
        message += p + "\n"
    send_telegram(message)

if __name__ == "__main__":
    run_bot()
