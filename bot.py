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
def save_history(total_profit):

    with open("history.txt", "a") as f:
        f.write(f"{total_profit}\n")

SECTOR_SENTIMENT = {
    "banking": "BULLISH",
    "fertilizer": "STABLE",
    "technology": "STRONG",
    "cement": "BEARISH"
}

def get_news(stock, sector):

    if sector == "banking":
        return "Banking sector improving after policy stability"

    elif sector == "technology":
        return "IT exports showing positive momentum"

    elif sector == "cement":
        return "Cement sector facing weak dispatches"

    elif sector == "fertilizer":
        return "Fertilizer demand remains stable"

    return "Market conditions neutral"

def generate_ai_summary(total_profit):

    if total_profit > 0:
        return (
            "🤖 DAILY AI SUMMARY\n"
            "Market sentiment improving.\n"
            "Portfolio remains in healthy condition.\n"
            "Recommended: Hold strong positions.\n"
        )

    else:
        return (
            "🤖 DAILY AI SUMMARY\n"
            "Market showing weakness.\n"
            "Risk management advised.\n"
            "Avoid aggressive buying.\n"
        )

def diversification_check(portfolio):

    sectors = {}

    for stock, info in portfolio.items():

        sector = info["sector"]

        if sector not in sectors:
            sectors[sector] = 0

        sectors[sector] += 1

    warnings = []

    for sector, count in sectors.items():

        if count >= 3:
            warnings.append(
                f"⚠ High exposure in {sector} sector"
            )

    return warnings
def calculate_health_score(total_profit, ranking):

    score = 50

    if total_profit > 0:
        score += 20

    if len(ranking) >= 5:
        score += 10

    positive = 0

    for stock, percent in ranking:

        if percent > 0:
            positive += 1

    score += positive * 3

    if score > 100:
        score = 100

    return score
def portfolio_allocation(portfolio):

    sectors = {}
    total_value = 0

    for stock, info in portfolio.items():

        sector = info["sector"]

        value = info["current_price"] * info["qty"]

        total_value += value

        if sector not in sectors:
            sectors[sector] = 0

        sectors[sector] += value

    allocation_text = "📊 PORTFOLIO ALLOCATION\n"

    for sector, value in sectors.items():

        percent = (value / total_value) * 100

        allocation_text += (
            f"{sector.upper()}: {round(percent,2)}%\n"
        )

    return allocation_text
def daily_change():

    try:

        with open("history.txt", "r") as f:

            lines = f.readlines()

        if len(lines) < 2:
            return "📅 DAILY CHANGE\nNot enough history data.\n"

        yesterday = float(lines[-2].strip())
        today = float(lines[-1].strip())

        change = today - yesterday

        emoji = "📈" if change >= 0 else "📉"

        return (
            f"📅 DAILY CHANGE\n"
            f"Yesterday Profit: {round(yesterday,2)} PKR\n"
            f"Today Profit: {round(today,2)} PKR\n"
            f"Change: {round(change,2)} PKR {emoji}\n"
        )

    except:
        return "📅 DAILY CHANGE\nHistory unavailable.\n"
def smart_alerts(portfolio):

    alerts = []

    for stock, info in portfolio.items():

        buy_price = info["buy_price"]
        current_price = info["current_price"]

        percent = (
            (current_price - buy_price)
            / buy_price
        ) * 100

        if percent > 10:
            alerts.append(
                f"🔥 {stock} hitting strong profit zone"
            )

        elif percent < -15:
            alerts.append(
                f"⚠️ {stock} showing heavy losses"
            )

    if not alerts:
        return "✅ No major alerts"

    return "\n".join(alerts)
    
def market_mood(total_profit, ranking):

    positive = 0

    for stock, percent in ranking:

        if percent > 0:
            positive += 1

    if total_profit > 0 and positive >= 4:
        return "📈 MARKET MOOD: BULLISH"

    elif total_profit > 0:
        return "📊 MARKET MOOD: MODERATELY BULLISH"

    else:
        return "📉 MARKET MOOD: BEARISH"
def analyze_portfolio(portfolio):

    results = []

    total_investment = 0
    current_value = 0
    total_profit = 0

    best_stock = ""
    best_percent = -999

    worst_stock = ""
    worst_percent = 999

    ranking = []

    for stock, info in portfolio.items():

        buy_price = info["buy_price"]
        current_price = info["current_price"]
        qty = info["qty"]
        sector = info["sector"]

        investment = buy_price * qty
        value = current_price * qty

        profit = value - investment
        percent = ((current_price - buy_price) / buy_price) * 100

        total_investment += investment
        current_value += value
        total_profit += profit
        
        ranking.append((stock, percent))

        # BEST/WORST STOCK

        if percent > best_percent:
            best_percent = percent
            best_stock = stock

        if percent < worst_percent:
            worst_percent = percent
            worst_stock = stock

        # TARGET & SL

        stop_loss = round(buy_price * 0.95, 2)
        target = round(buy_price * 1.10, 2)

        confidence = 50
        action = "HOLD"
        reason = ""
        sentiment = SECTOR_SENTIMENT.get(sector, "NEUTRAL")
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

        # DYNAMIC AI CONFIDENCE

        if percent > 10:
           confidence += 20

        elif percent > 5:
             confidence += 15

        elif percent > 0:
             confidence += 8

        elif percent < -10:
             confidence -= 10


        if percent > 10:
          action = "SELL PARTIAL"    

        # SECTOR LOGIC

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

        # RISK METER

        if percent < -15:
            risk = "HIGH RISK"

        elif percent < -5:
            risk = "MEDIUM RISK"

        else:
            risk = "LOW RISK"

        # EMOJI

        if percent >= 0:
            emoji = "🟢"
        else:
            emoji = "🔴"
        news = get_news(stock, sector)
        results.append(
            f"{emoji} {stock} → {action}\n"
            f"Profit: {round(percent,2)}%\n"
            f"Target: {target}\n"
            f"SL: {stop_loss}\n"
            f"Risk: {risk}\n"
            f"Sector Sentiment: {sentiment}\n"
            f"Reason: {reason}\n"
            f"News: {news}\n"
            f"Confidence: {confidence}%\n"
        )
        
    # SORT RANKING

    ranking.sort(key=lambda x: x[1], reverse=True)

    # SAVE DAILY HISTORY

    save_history(round(total_profit,2))

    # SUMMARY

    summary = (
        f"📈 PORTFOLIO SUMMARY\n"
        f"💰 Total Investment: {round(total_investment,2)} PKR\n"
        f"💵 Current Value: {round(current_value,2)} PKR\n"
        f"📊 Net Profit: {round(total_profit,2)} PKR\n"
        f"📈 Best Performer: {best_stock} ({round(best_percent,2)}%)\n"
        f"📉 Worst Performer: {worst_stock} ({round(worst_percent,2)}%)\n\n"
    )

    # RANKING

    ranking_text = "🏆 PORTFOLIO RANKING\n"

    for i, r in enumerate(ranking, start=1):

        ranking_text += (
            f"{i}. {r[0]} ({round(r[1],2)}%)\n"
        )

    ai_summary = generate_ai_summary(total_profit)
    
    health_score = calculate_health_score(total_profit, ranking)

    allocation = portfolio_allocation(portfolio)

    daily_tracker = daily_change()
    
    alerts = smart_alerts(portfolio)
    
    market_status = market_mood(total_profit, ranking)
    
    health_text = (
    f"🧠 AI HEALTH SCORE: {health_score}/100\n"
    )
    warnings = diversification_check(portfolio)

    warning_text = ""

    for w in warnings:
        warning_text += w + "\n"

    results.insert(0, market_status)
    results.insert(0, alerts)
    results.insert(0, daily_tracker)
    results.insert(0, allocation)
    results.insert(0, health_text)
    results.insert(0, warning_text)
    results.insert(0, ai_summary)
    results.insert(0, ranking_text)
    results.insert(0, summary)

    return results

        

def run_bot():

    portfolio_report = analyze_portfolio(portfolio)

    message = "📊 AI PORTFOLIO REPORT\n\n"

    for p in portfolio_report:
        message += p + "\n"

    send_telegram(message)


if __name__ == "__main__":
    run_bot()


