from playwright.sync_api import sync_playwright
from queue import Queue
from threading import Thread
import time
import os
import requests

THREADCOUNT = 10
queue = Queue()
notTaken = []

usernames_to_check = [
  "SunsetEstates", "SunsetVillas", "SunsetHomes", "SunsetProperties",
  "SunsetResidences", "SunsetHavens", "SunsetMansions", "SunsetCondos",
  "SunsetRetreats", "SunsetRealEstate", "SunsetLiving", "SunsetOasis",
  "SunsetParadise", "SunsetManor", "SunsetHeights", "SunsetDwellings",
  "SunsetGardens", "SunsetLofts", "SunsetTerraces", "SunsetViews",
  "PremiumEstates", "PremiumVillas", "PremiumHomes", "PremiumProperties",
  "PremiumResidences", "PremiumHavens", "PremiumMansions", "PremiumCondos",
  "PremiumRetreats", "PremiumRealEstate", "PremiumLiving", "PremiumOasis",
  "PremiumParadise", "PremiumManor", "PremiumHeights", "PremiumDwellings",
  "PremiumGardens", "PremiumLofts", "PremiumTerraces", "PremiumViews",
  "EmpireEstates", "EmpireVillas", "EmpireHomes", "EmpireProperties",
  "EmpireResidences", "EmpireHavens", "EmpireMansions", "EmpireCondos",
  "EmpireRetreats", "EmpireRealEstate", "EmpireLiving", "EmpireOasis",
  "EmpireParadise", "EmpireManor", "EmpireHeights", "EmpireDwellings",
  "EmpireGardens", "EmpireLofts", "EmpireTerraces", "EmpireViews"
]

def is_username_taken(username):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        url = f"https://www.instagram.com/{username}/"
        page.goto(url)
        
        # Wait for the page to load
        time.sleep(1)
        body_text = page.text_content("body")
        browser.close()

        if "Sorry, this page isn't available." in body_text:
            return False
        return True

def check_domain_availability(domain):
    try:
        response = requests.get(f"http://{domain}")
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False

def DoWork(line):
    base_username = line.replace(".", "").replace("_", "")
    if not is_username_taken(line):
        notTaken.append(line)
        print(f"{line} ✅", end=" ")
        domain = f"{base_username}.com"
        if check_domain_availability(domain):
            print(f"{domain} ❌")
        else:
            print(f"{domain} ✅")
    else:
        print(f"{line} ❌")

def Worker(q):
    while True:
        line = q.get()
        DoWork(line)
        time.sleep(1)
        q.task_done()

for i in range(THREADCOUNT):
    worker = Thread(target=Worker, args=(queue,))
    worker.setDaemon(True)
    worker.start()

def main():
    for Account in usernames_to_check:
        queue.put(Account)

    queue.join()

    for a in notTaken:
        with open('Working.txt', 'w+') as File:
            for i in notTaken:
                File.write(i + '\n')

    print('Saved to {0}./Working.txt'.format(os.getcwd()))

if __name__ == '__main__':
    main()
