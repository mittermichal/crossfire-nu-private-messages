#!/usr/bin/env python
# coding: utf-8

"""
Script to scrape private messages from https://crossfire.nu
Author: Michal Mitter mittermichal@protonmail.com
"""

import requests
import sys
from bs4 import BeautifulSoup
import getpass
import re
import json

s = requests.Session()

email = input("Type email:")
password = getpass.getpass("Type password:")

login = s.post(
    'https://www.crossfire.nu/user/login', 
    data={
        "identity": email,
        "credentials": password,
        "login": " Log+In",
        "cookie": [
            "0",
            "1"
        ]
    }
)
soup = BeautifulSoup(login.text, features="html.parser")

errors = soup.find("ul", "errors")

if errors or login.status_code != 200:
    print(errors.text, file=sys.stderr)
    exit(-1)

print("Login successful")


def get_pms(url, subject_class):
    print("Downloading", url)
    last_page_res = s.get(url)
    soup = BeautifulSoup(last_page_res.text, features="html.parser")

    page = 1
    while True:
        print(f"Page: {page}")
        content = soup.find(id="content")
        pm_rows = content.find("table", {"class": "list"}).find("tbody").find_all("tr")
        
        for pm in pm_rows:
            pm_url = "https://www.crossfire.nu" + pm.find("td", subject_class).a["href"]
            pm_res = s.get(pm_url)
            pm_text = str(BeautifulSoup(pm_res.text, features="html.parser").find("div", {"class": "bb-container"}))
            contacts = [{
                "id": re.search(r'\d+', contact_elem["href"])[0],
                "name": contact_elem.text         
                } 
                for contact_elem in pm.find("td", {"class": "contact"}).find_all("a", {"class": "user"})
            ]
            subject_text = pm.find("td", subject_class).text
            pm_obj = {
                "contacts": contacts,
                "subject": re.sub(r'^\n(.*)\n$', r'\1', subject_text),  # clean \n from start and end
                "date": pm.find("td", {"class": "date"}).text,
                "text": pm_text
            }
            yield pm_obj
        next_page_element = content.find("a", {"title": "Go To Next Page"})
        if not next_page_element:
            break
        soup = BeautifulSoup(s.get("https://www.crossfire.nu" + next_page_element["href"]).text, features="html.parser")
        page += 1


filename = "crossfire-messages.json"
inbox = list(get_pms("https://www.crossfire.nu/private-message", "subject"))
outbox = list(get_pms("https://www.crossfire.nu/private-message/sent", "title"))

with open(filename, 'w') as f:
    messages = {
        "inbox": inbox,
        "outbox": outbox
    }
    json.dump(messages, f, indent=2)
print(f"{len(inbox)} inbox and {len(outbox)} outbox messages saved to {filename}.")
