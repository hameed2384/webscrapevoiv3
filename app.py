from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import os

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from any domain

def fetch_current_time():
    try:
        london_time = datetime.now(pytz.timezone("Europe/London"))
        return london_time.strftime("%H:%M")
    except Exception:
        return "Time unavailable"

def fetch_prayer_times():
    url = "https://khuddam.org.uk/salat/"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        section = soup.find("h3", string="Baitul Futuh")
        if not section:
            return {}
        timings = {}
        for li in section.find_next("ul", class_="timing--shedule").find_all("li"):
            hour = li.contents[0].strip()
            minute = li.contents[2].strip()
            name = li.find("span", class_="time--name").text.strip()
            full_time = f"{hour}:{minute}"
            timings[name] = full_time
        return timings
    except Exception:
        return {}

def fetch_weather():
    url = "https://weather.com/en-GB/weather/today/l/0b8697c01baca04214b4abd206319d3eba60db5fb05c191012c4e02f6bdb23a4"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        temp_main = soup.select_one("span[data-testid='TemperatureValue']")
        return {
            "temperature": temp_main.get_text(strip=True) if temp_main else "N/A"
        }
    except Exception:
        return {}

def fetch_schedule():
    url = "https://voiceofislam.co.uk/show-schedule/"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.select("div.qt-part-show-schedule-day-item")
        schedule = []
        for item in items:
            day = item.select_one("span.qt-day")
            time = item.select_one("span.qt-time")
            title = item.select_one("h4 a.qt-t")
            if day and time and title:
                schedule.append({
                    "day": day.text.strip(),
                    "time": time.text.strip(),
                    "title": title.text.strip()
                })
        return schedule
    except Exception:
        return []

@app.route("/api/home")
def home():
    return jsonify({
        "current_time": fetch_current_time(),
        "prayers": fetch_prayer_times(),
        "schedule": fetch_schedule(),
        "weather": fetch_weather()
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
