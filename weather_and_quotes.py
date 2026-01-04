# this code displays current weather and a quote from zenquotes every 30 mins on my desk
# m5stack

from m5stack import *
from m5ui import *
import urequests
import time
import wifiCfg


LAT = 33.2148
LON = -97.1331
CITY = "Denton, TX"  #my location, TODO: better to track with ip

REFRESH_SECONDS = 30 * 60  # 30 minutes


try:
    WEATHER_FONT = lcd.FONT_DejaVu18
    QUOTE_FONT = lcd.FONT_DejaVu24
except:
    WEATHER_FONT = lcd.FONT_Default
    QUOTE_FONT = lcd.FONT_Default


setScreenColor(0x000000)
lcd.setBrightness(60)

SCREEN_W, SCREEN_H = lcd.winsize()
WEATHER_HEIGHT = 60
PADDING = 8

weather_box = M5TextBox(PADDING, 6, "", WEATHER_FONT, 0x00FFAA)
quote_box = M5TextBox(PADDING, WEATHER_HEIGHT + 6, "", QUOTE_FONT, 0xFFFFFF)


def draw_divider():
    lcd.line(0, WEATHER_HEIGHT, SCREEN_W, WEATHER_HEIGHT, 0x444444)


lcd.print("Connecting WiFi..", 10, SCREEN_H - 20)

if not wifiCfg.is_connected():
    wifiCfg.autoConnect()

# wait till its connected
while not wifiCfg.is_connected():
    time.sleep(1)

lcd.clear(0x000000)


def wrap_text(text, max_chars=22):
    words = text.split(" ")
    lines = []
    line = ""

    for word in words:
        if not line:
            line = word
        elif len(line) + 1 + len(word) <= max_chars:
            line = line + " " + word
        else:
            lines.append(line)
            line = word

    if line:
        lines.append(line)

    return "\n".join(lines)


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

        return "{}\n{}°C  |  {}  | {} km/h".format(
            CITY, temp, desc, wind
        )
    except:
        return "{}\nWeather unavailable".format(CITY)


def fetch_quote(): # get random quotes from zenquotes api
    try:
        r = urequests.get("https://zenquotes.io/api/random")
        j = r.json()
        r.close()

        quote = j[0]["q"]
        author = j[0]["a"]

        return "{}\n- {}".format(quote, author)
    except:
        return "Stay present.\n- Unknown"


while True:
    lcd.clear(0x000000)

    weather_text = fetch_weather()
    quote_text = fetch_quote()

    weather_box.setText(weather_text)
    draw_divider()
    quote_box.setText(wrap_text(quote_text))

    time.sleep(REFRESH_SECONDS)
