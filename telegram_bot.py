import os
import requests

BOT_TOKEN=os.environ["BOT_TOKEN"]
CHAT_ID=os.environ["CHAT_ID"]

def send_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    print(requests.get(url).json()) # this sends the message

def main():
    message = "hello from your telegram bot"
    send_message(message)

if __name__ == '__main__':
    main()