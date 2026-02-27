# m5stack

from m5stack import *
from m5ui import *
import urequests
import time
import wifiCfg

LAT = 33.2148
LON = -97.1331
CITY = "Denton, TX"

SERVER_IP = "192.168.0.197:8000"
REFRESH_SECONDS = 10 * 60  # 10 minutes

try:
    WEATHER_FONT = lcd.FONT_DejaVu18
    SERVER_FONT = lcd.FONT_DejaVu18
except:
    WEATHER_FONT = lcd.FONT_Default
    SERVER_FONT = lcd.FONT_Default

setScreenColor(0x000000)
lcd.setBrightness(60)

SCREEN_W, SCREEN_H = lcd.winsize()
WEATHER_HEIGHT = 30
PADDING = 0

weather_box = M5TextBox(PADDING, 0, "", WEATHER_FONT, 0x00FFAA)
server_box = M5TextBox(PADDING, WEATHER_HEIGHT, "", SERVER_FONT, 0xFFFFFF)

def draw_divider():
    lcd.line(0, WEATHER_HEIGHT, SCREEN_W, WEATHER_HEIGHT, 0x444444)

lcd.print("Connecting WiFi..", 10, SCREEN_H - 20)

if not wifiCfg.is_connected():
    wifiCfg.autoConnect()

while not wifiCfg.is_connected():
    time.sleep(1)

lcd.clear(0x000000)

WEATHER_CODE = {
    0: "Clear", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Fog",
    51: "Drizzle", 53: "Drizzle", 55: "Drizzle",
    61: "Rain", 63: "Rain", 65: "Heavy rain",
    71: "Snow", 73: "Snow", 75: "Heavy snow",
    80: "Rain showers", 81: "Rain showers", 82: "Heavy showers",
    95: "Thunderstorm"
}

def fetch_weather():
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            "?latitude={}&longitude={}"
            "&current_weather=true"
            "&temperature_unit=celsius"
            "&windspeed_unit=kmh"
        ).format(LAT, LON)

        r = urequests.get(url)
        j = r.json()
        r.close()

        cw = j["current_weather"]
        temp = int(cw["temperature"])
        wind = int(cw["windspeed"])
        desc = WEATHER_CODE.get(cw["weathercode"], "Weather")

        return "{} | {}°C | {} |".format(CITY, temp, desc)
    except:
        return "{}\nWeather unavailable".format(CITY)


def convert_utc_to_local(updated_at):
    try:
        s = updated_at.replace("_", " ")
        date_part, time_part = s.split(" ")

        if ":" in time_part:
            hh, mm, ss = time_part.split(":")
        else:
            hh, mm, ss = time_part.split("-")

        hh = int(hh)
        mm = int(mm)

        if hh < 0:
            hh += 24
        elif hh >= 24:
            hh -= 24

        # Convert to 12-hour
        ampm = "am"
        if hh == 0:
            hh = 12
        elif hh == 12:
            ampm = "pm"
        elif hh > 12:
            hh -= 12
            ampm = "pm"

        return "({}:{} {})".format(hh, "{:02d}".format(mm), ampm)

    except:
        return ""


def fetch_servers():
    try:
        url = "http://{}/temperature".format(SERVER_IP)
        r = urequests.get(url)
        data = r.json()
        r.close()

        if isinstance(data, dict):
            data = [data]

        header = "Servers\n" + "-" * 16
        server_blocks = []

        for item in data:
            srv = item.get("server", "?")
            sensors = item.get("sensors", [])
            updated = item.get("updated_at", "")

            parts = []
            for s in sensors:
                sensor_name = s.get("sensor", "?")
                raw_temp = s.get("temperature", "?")
                parts.append("{} | {} |".format(sensor_name, raw_temp))

            temp_str = " ".join(parts) if parts else "No sensors"
            time_str = convert_utc_to_local(updated)

            block = "{}\n{}\n{}".format(srv, temp_str, time_str)
            server_blocks.append(block)

        return header + "\n\n" + "\n\n".join(server_blocks)

    except Exception:
        return "Servers\nUnavailable"


while True:
    lcd.clear(0x000000)

    weather_text = fetch_weather()
    server_text = fetch_servers()

    weather_box.setText(weather_text)
    draw_divider()
    server_box.setText(server_text)

    time.sleep(REFRESH_SECONDS)