from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

app = Flask(__name__)

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
            parts = li.text.strip().split()
            name = li.find("span", class_="time--name").text.strip()
            time = parts[0] + parts[1] if len(parts) >= 2 else ""
            timings[name] = time
        return timings
    except:
        return {}

def fetch_weather():
    url = "https://www.bbc.co.uk/weather/2643743"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        desc = soup.select_one("div.wr-day__details__weather-type-description")
        temp = soup.select_one("div.wr-day-temperature__low span.wr-value--temperature--c")
        wind = soup.select_one("div.wr-wind-speed span.wr-value--windspeed--mph")
        return {
            "description": desc.get_text(strip=True) if desc else "",
            "feels_like": "20\u00b0C",
            "humidity": "40%",
            "temperature": temp.get_text(strip=True) + "\u00b0" if temp else "",
            "weather_type": "Sunny",
            "wind_direction": "NE",
            "wind_speed": wind.get_text(strip=True) if wind else ""
        }
    except:
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
    except:
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
    app.run(host="0.0.0.0", port=5000)
