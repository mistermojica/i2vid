from playwright.sync_api import sync_playwright
import time
import os
import requests

notTaken = []

usernames_to_check = [
    "BestRentals",
    "BestHomes",
    "BestVillas",
    "BestMansions",
    "BestRetreats",
    "BestEstates",
    "BestResidences",
    "BestSuites",
    "BestCondos",
    "BestApartments"
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

def DoWork(line, index):
    base_username = line.replace(".", "").replace("_", "")
    
    username_available = not is_username_taken(line)
    domain_available = not check_domain_availability(f"{base_username}.com")

    if username_available:
        notTaken.append(line)
        print(f"{index}. {line} ✅", end=" ")
    else:
        print(f"{index}. {line} ❌", end=" ")
    
    domain = f"{base_username}.com"
    if domain_available:
        print(f"{domain} ✅")
    else:
        print(f"{domain} ❌")

def main():
    for index, Account in enumerate(usernames_to_check, start=1):
        DoWork(Account, index)
        time.sleep(1)  # Adding a delay to avoid being rate limited

    with open('Working.txt', 'w+') as File:
        for i in notTaken:
            File.write(i + '\n')

    print('Saved to {0}./Working.txt'.format(os.getcwd()))

if __name__ == '__main__':
    main()
