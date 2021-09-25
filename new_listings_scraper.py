from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from chromedriver_py import binary_path
import os.path, json

from store_order import *
from load_config import *
from send_notification import *


chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(executable_path=binary_path, options=chrome_options)
driver.get("https://www.binance.com/en/support/announcement/c-48")


def get_last_coin():
    """
    Scrapes new listings page for and returns new Symbol when appropriate
    """
    latest_announcement = driver.find_element(By.ID, 'link-0-0-p1')
    latest_announcement = latest_announcement.text

    # Binance makes several annoucements, irrevelant ones will be ignored
    exclusions = ['Futures', 'Margin', 'adds']
    for item in exclusions:
        if item in latest_announcement:
            return None
    enum = [item for item in enumerate(latest_announcement)]
    #Identify symbols in a string by using this janky, yet functional line
    uppers = ''.join(item[1] for item in enum if item[1].isupper() and (enum[enum.index(item)+1][1].isupper() or enum[enum.index(item)+1][1]==' ' or enum[enum.index(item)+1][1]==')') )

    return uppers


def store_new_listing(listing):
    """
    Only store a new listing if different from existing value
    """

    if os.path.isfile('new_listing.json'):
        file = load_order('new_listing.json')
        if listing in file:
            print("No new listings detected...")

            return file
        else:
            file = listing
            store_order('new_listing.json', file)
            #print("New listing detected, updating file")
            send_notification(listing)
            return file

    else:
        new_listing = store_order('new_listing.json', listing)
        send_notification(listing)
        #print("File does not exist, creating file")

        return new_listing


def search_and_update():
    """
    Pretty much our main func
    """
    while True:
        latest_coin = get_last_coin()
        if latest_coin:
            store_new_listing(latest_coin)
        else:
            pass
        print("Checking for coin announcements every 2 hours (in a separate thread)")
        return latest_coin
        time.sleep(60*180)
