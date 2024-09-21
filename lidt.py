import requests
from requests.cookies import RequestsCookieJar
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import time
from time import gmtime, strftime
import os
import urllib3
from datetime import datetime
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

def extract_and_format_date_time(text):
    match = re.match(r'(\w{3}) (\d{1,2})(?:st|nd|rd|th)?(\w{3})(\d{2}:\d{2})', text)
    if match:
        day_of_week, day, month, time = match.groups()
        month = datetime.strptime(month, '%b').strftime('%b')
        return f"{day_of_week} {day} {month} {time}"
    return ""

old_list = []
current_list = []
os_clear = True

while True:
    proxies = {
        "http": "PROXIES"
    }

    url = "https://lidt.co.uk/fast-track-booking"

    response = session.get(url, verify=False, proxies=proxies)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    current_list.clear()
    elements = soup.find_all("button", {"data-centre": "Crawley Crawley"})
    
    current_list.extend([extract_and_format_date_time(test.get_text()) for test in elements])

    for i in current_list:
        if i not in old_list and i:
            print("NEW AVAILABLE TEST:  " + i + "     " + "Found at: " + datetime.now().strftime('%H:%M'))
            print("Current available tests:  " + str(current_list))
            for u in elements:
                if i in str([extract_and_format_date_time(u.get_text())]):
                    print("Booking link:  " + "https://lidt.co.uk/booking?type=test&id=" + u["id"]  + "   " + str([extract_and_format_date_time(u.get_text())]))
                    print(" ")
            url = "https://lidt.co.uk/booking?type=test&id=" + u["id"]

            payload = {
                "type": "test",
                "id": str(u["id"])
            }

            if os_clear != True:
                r = requests.post(url, data=payload, proxies=proxies)

                cookie_jar = r.cookies
                for cookie in cookie_jar:
                    print(f'document.cookie = "{cookie.name}={cookie.value}; path=/";')
                print("^^ Go onto lidt, inspect element and paste these in the 'console' tab and press enter. Then reload the link for the booking. ^^")
            print("-------------------------------------------")

    for i2 in old_list:
        if i2 not in current_list and i2:
            print("TEST HAS BEEN AUTO BOOKED:  " + i2 + "     " + "Found at: " + datetime.now().strftime('%H:%M'))
            print("Current available tests:  " + str(current_list))
            print("-------------------------------------------")

    old_list.clear()
    old_list.extend(current_list)
    time.sleep(2)

    if os_clear == True:
        print("^^ !! IGNORE THESE !! ^^")
        print(" ")
        print("-- NEW TESTS PRINTED BELOW --")
    os_clear = False

