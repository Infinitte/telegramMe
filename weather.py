import os
import requests
import telegram_bot

OWM_KEY=os.environ["OWM_KEY"]
LATITUDE="37.41"
LONGITUDE="-5.99"

def get_data():
    '''
    Returns tres outputs:
    - Rain: True if rains, False in other case
    - City
    - Weather Description
    '''
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LATITUDE}&lon={LONGITUDE}&appid={OWM_KEY}"
    res = requests.get(url).json()
    tomorrow = res["list"][2]
    city = res["city"]["name"]
    if "rain" in tomorrow:
        return True,city,tomorrow["weather"][0]["description"]
    else:
        return False,city,tomorrow["weather"][0]["description"]


def main():
    rain,city,description=get_data()
    if rain:
        telegram_bot.send_message(f"Tomorrow forecast is {description} in {city}. Take care")

if __name__ == '__main__':
    main()