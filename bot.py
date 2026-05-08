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

portfolio = {
    "FATIMA": {
        "buy_price": 141.86,
        "current_price": 137.43,
        "qty": 500,
        "sector": "fertilizer"
    },

    "HBL": {
        "buy_price": 289.43,
        "current_price": 295.26,
        "qty": 600,
        "sector": "banking"
    },

    "MEBL": {
        "buy_price": 430.65,
        "current_price": 485.95,
        "qty": 610,
        "sector": "banking"
    },

    "MLCF": {
        "buy_price": 106.59,
        "current_price": 88.96,
        "qty": 750,
        "sector": "cement"
    },

    "SYS": {
        "buy_price": 149.34,
        "current_price": 153.89,
        "qty": 345,
        "sector": "technology"
    },

    "UBL": {
        "buy_price": 392.08,
        "current_price": 415.22,
        "qty": 250,
        "sector": "banking"
    }
}
def analyze_portfolio(portfolio):

    results = []
    total_profit = 0

    for stock, info in portfolio.items():

        buy_price = info["buy_price"]
        current_price = info["current_price"]
        qty = info["qty"]
        sector = info["sector"]

        profit = (current_price - buy_price) * qty
        percent = ((current_price - buy_price) / buy_price) * 100

        total_profit += profit

        stop_loss = round(buy_price * 0.95, 2)
        target = round(buy_price * 1.10, 2)

        confidence = 65
        action = "HOLD"
        reason = ""

        # AI STYLE LOGIC

        if percent > 10:
            action = "SELL PARTIAL"
            confidence = 78
            reason = "Strong profit booked"

        elif percent > 3:
            action = "HOLD"
            confidence = 72
            reason = "Uptrend remains healthy"

        elif percent < -10:
            action = "BUY MORE"
            confidence = 70
            reason = "Stock heavily discounted"

        elif percent < -5:
            action = "HOLD"
            confidence = 60
            reason = "Temporary weakness"

        # Sector intelligence

        if sector == "banking":
            confidence += 5
            reason += " | Banking sector improving"

        elif sector == "fertilizer":
            confidence += 3
            reason += " | Fertilizer sector stable"

        elif sector == "technology":
            confidence += 4
            reason += " | IT exports improving"

        elif sector == "cement":
            confidence -= 3
            reason += " | Cement sector weak"

        results.append(
            f"{stock} → {action}\n"
            f"Profit: {round(percent,2)}%\n"
            f"Target: {target}\n"
            f"SL: {stop_loss}\n"
            f"Reason: {reason}\n"
            f"Confidence: {confidence}%\n"
        )

    results.append(f"💰 TOTAL PROFIT: {round(total_profit,2)} PKR")

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

                else:
                    if score >= 0:
                        r["signal"] = "BUY 🔥"
                        r["confidence"] = 50
                        top_buy.append(r)
                    else:
                        r["signal"] = "SELL ⚠️"
                        r["confidence"] = 50
                        top_sell.append(r)

        except Exception as e:
            print("Error:", e)
            continue

    portfolio = load_portfolio()
    portfolio_report = analyze_portfolio(portfolio)

    message = "📊 PSX FINAL REPORT\n\n"

    message += "🟢 TOP BUY:\n"
    if not top_buy:
        message += "No BUY signals ⚠️\n"
    else:
        for r in top_buy:
            message += f"{r['stock']} | Price:{r['price']} | Score:{r['score']} | Conf:{r['confidence']}%\n"

    message += "\n🔴 TOP SELL:\n"
    if not top_sell:
        message += "No SELL signals ⚠️\n"
    else:
        for r in top_sell:
            message += f"{r['stock']} | Price:{r['price']} | Score:{r['score']} | Conf:{r['confidence']}%\n"

    message += "\n💼 YOUR PORTFOLIO:\n"
    for p in portfolio_report:
        message += p + "\n"

    send_telegram(message)

if __name__ == "__main__":
    run_bot()
