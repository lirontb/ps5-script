from typing import List
from bs4 import BeautifulSoup
import requests
import json
import smtplib, ssl
from datetime import datetime
from time import sleep
from random import randint


def handle_blacklist(content: str, blacklist: List[str]) -> bool:
    if len(blacklist) == 0:
        return False

    for keyword in blacklist:
        if keyword in content:
            return False
    return True


def handle_whitelist(content: str, whitelist: List[str]) -> bool:
    if len(whitelist) == 0:
        return False

    for keyword in whitelist:
        if keyword in content:
            return True
    return False


def send_mail(message: str) -> None:
    port = 465  # For SSL
    smtp_server = "smtp"
    sender_email = "ps5@script.com"  # Enter your address
    # Enter receiver address
    receivers_email = ["your@mail.com"]
    password = "*****"
    message = f"""\
    Subject: PS5 DETECTED!

    {message}

    This message is sent from Python."""

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server) as server:
        #server.login(sender_email, password)
        server.sendmail(sender_email, receivers_email, message)


def main(file: str) -> None:
    with open(file, "r") as f:
        data = json.load(f)

        for site in data:
            url = site['url']
            print(f"{datetime.now().isoformat()} Checking: {url}")
            try:
                r = requests.get(url)
                if r.status_code > 299 or r.status_code < 200:
                    continue

                whitelist = site.get('whitelist', [])
                blacklist = site.get('blacklist', [])
                soup = site.get('soup', {})

                content = r.text.lower()

                if len(soup) > 0:
                    content = BeautifulSoup(content, "html.parser").find(soup["tag"], {soup["property"]: soup["value"]})  # noqa: E501

                notify = handle_whitelist(content, whitelist) or handle_blacklist(content, blacklist) and "overload.jpg" not in content  # noqa: E501

                if notify:
                    print(f"{datetime.now().isoformat()} THERE IS A MATCH!: {url}")
                    send_mail(f"{datetime.now().isoformat()} THERE IS A MATCH!: {url}")
            except:  # noqa: E722
                print(f"{datetime.now().isoformat()} Url: {url} is not working")
                continue


while True:
    main("website.json")
    sleep(randint(1, 5) * 60)
