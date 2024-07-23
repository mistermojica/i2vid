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
  "OasisResidences", "SunshineEstates", "MillennialManor", "LuxuryLiving",
  "CoastalDreams", "InnovativeLiving", "EliteNest", "PalmGrove",
  "HarborView", "BreezeBay", "SapphireShores", "GoldenCoast",
  "ChicHaven", "PremiumParadise", "ModernHaven", "TranquilOasis",
  "SunnySide", "YoungProfessional", "LuxuriousLiving", "CoastalResidences",
  "InnovativeSpaces", "EliteLiving", "PalmHomes", "HarborEstates",
  "BreezeHomes", "SapphireLiving", "GoldenEstates", "ChicResidences",
  "PremiumHomes", "ModernEstates", "OasisHaven", "SunshineHaven",
  "MillennialNest", "LuxuryEstates", "CoastalLiving", "InnovativeManor",
  "EliteGrove", "PalmNest", "HarborGrove", "BreezeHaven",
  "SapphireParadise", "GoldenHaven", "ChicParadise", "PremiumShores",
  "ModernParadise", "OasisGrove", "SunshineNest", "MillennialParadise",
  "LuxuryHaven", "CoastalShores", "InnovativeGrove", "EliteParadise",
  "PalmShores", "HarborParadise", "BreezeNest", "SapphireGrove",
  "GoldenParadise", "ChicShores", "PremiumGrove", "ModernNest",
  "OasisParadise", "SunshineGrove", "MillennialShores", "LuxuryGrove",
  "CoastalNest", "InnovativeShores", "EliteGrove", "PalmParadise",
  "HarborNest", "BreezeGrove", "SapphireNest", "GoldenShores",
  "ChicNest", "PremiumHaven", "ModernShores", "OasisNest",
  "SunshineParadise", "MillennialGrove", "LuxuryNest", "CoastalGrove",
  "InnovativeParadise", "EliteHaven", "PalmHaven", "HarborShores",
  "BreezeParadise", "SapphireNest", "GoldenNest", "ChicGrove",
  "PremiumNest", "ModernGrove", "OasisShores", "SunshineHaven",
  "MillennialLiving", "LuxuryParadise", "CoastalHaven", "InnovativeNest",
  "EliteParadise", "PalmHaven", "HarborNest", "BreezeHaven",
  "SapphireGrove"
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
    username_taken = is_username_taken(line)
    domain_taken = check_domain_availability(f"{base_username}.com")
    
    if not username_taken:
        notTaken.append(line)
    
    username_status = "✅" if not username_taken else "❌"
    domain_status = "✅" if not domain_taken else "❌"
    
    print(f"{line} {username_status} {base_username}.com {domain_status}")
    
    with open('Working.txt', 'a') as file_working:
        if not username_taken:
            file_working.write(f"{line}\n")
    
    with open('BothAvailable.txt', 'a') as file_both:
        if not username_taken and not domain_taken:
            file_both.write(f"{line}\n")

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

    print(f'Saved to {os.getcwd()}/Working.txt and {os.getcwd()}/BothAvailable.txt')

if __name__ == '__main__':
    main()
