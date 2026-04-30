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
SYMBOL_MAP = {
    "UBL": "united-bank-ltd",
    "HBL": "habib-bank-ltd",
    "MEBL": "meezan-bank",
    "ENGRO": "engro-corp",
    "PSO": "pakistan-state-oil",
    "MCB": "mcb-bank",
    "LUCK": "lucky-cement",
    "FFC": "fauji-fertilizer",
    "POL": "pakistan-oilfields",
    "OGDC": "oil-and-gas-development",
    "SNGP": "sui-northern-gas",
    "SYS": "systems-ltd",
    "TRG": "trg-pakistan",
    "PIOC": "piochre-pakistan",
    "DGKC": "dg-khan-cement",
    "BAHL": "bank-alfalah",
    "EFERT": "engro-fertilizers",
    "HUBC": "hub-power",
    "NML": "nishat-mills",
    "NBP": "national-bank-pakistan",
    "KEL": "k-electric"
}
def get_data(symbol):
    import time

    name = SYMBOL_MAP.get(symbol, symbol.lower())
    url = f"https://www.investing.com/equities/{name}-historical-data"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for attempt in range(3):
        try:
            res = requests.get(url, headers=headers)

            if res.status_code != 200:
                print(symbol, "Failed attempt", attempt+1)
                time.sleep(2)
                continue

            tables = pd.read_html(res.text)

            if not tables:
                print(symbol, "No table ❌")
                return None

            df = tables[0]

            df = df.rename(columns={"Price": "Close"})
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date")

            df["Close"] = df["Close"].astype(str).str.replace(",", "").astype(float)

            return df

        except Exception as e:
            print(symbol, "Error:", e)
            time.sleep(2)

    return None

def analyze(stock):
    df = get_data(stock)

    if df is None or len(df) < 30:
        print(stock, "Using fallback data")
        df = pd.DataFrame({
            "Date": pd.date_range(end=pd.Timestamp.today(), periods=50),
            "Close": [100 + i for i in range(50)]
        })

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

def load_portfolio():
    with open("portfolio.json") as f:
        return json.load(f)

def run_bot():
    results = []
    top_buy = []
    top_sell = []
    for stock in STOCKS:
       try:
           r = analyze(stock)

           if r:
               score = r["score"]

               if score >= 2:
                  r["signal"] = "BUY 🔥"
                  r["confidence"] = min(score * 20, 90)
                  top_buy.append(r)

               elif score <= -2:
                  r["signal"] = "SELL ⚠️"
                  r["confidence"] = min(abs(score) * 20, 90)
                  top_sell.append(r)

        except Exception as e:
            print("Error:", e)
            continue

    portfolio = load_portfolio()
    portfolio_report = analyze_portfolio(portfolio)

    message = "📊 PSX FINAL REPORT\n\n"

    # 🟢 TOP BUY
    message += "🟢 TOP BUY:\n"
    if not top_buy:
        message += "No BUY signals ⚠️\n"
    else:
        for r in top_buy:
            message += f"{r['stock']} | Price:{r['price']} | Score:{r['score']} | Conf:{r['confidence']}%\n"

    # 🔴 TOP SELL
    message += "\n🔴 TOP SELL:\n"
    if not top_sell:
        message += "No SELL signals ⚠️\n"
    else:
        for r in top_sell:
            message += f"{r['stock']} | Price:{r['price']} | Score:{r['score']} | Conf:{r['confidence']}%\n"

    # 💼 PORTFOLIO
    message += "\n💼 YOUR PORTFOLIO:\n"
    for p in portfolio_report:
        message += p + "\n"

    send_telegram(message)

if __name__ == "__main__":
    run_bot()
