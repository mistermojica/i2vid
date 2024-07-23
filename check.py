import requests
from bs4 import BeautifulSoup
import time

def is_username_taken(username):
    url = f"https://www.instagram.com/{username}/"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        span = soup.find('span', string="Sorry, this page isn't available.")
        print("span", span)

        if span:
            return False
        return True
    return False

def check_usernames(usernames):
    results = {}
    for username in usernames:
        is_taken = is_username_taken(username)
        results[username] = is_taken
        if is_taken:
            print(f"The username '{username}' is already taken.")
        else:
            print(f"The username '{username}' is available.")
        time.sleep(1)  # Adding a delay to avoid being rate limited
    return results

if __name__ == "__main__":
    usernames_to_check = [
        "ALSDKFJADFLDKLuxuryTour", "LuxuryTravel", "LuxuryAdventures", "LuxuryEscapes", 
        "LuxuryJourneys", "LuxuryVacations", "LuxuryWander", "LuxuryExplore", 
        "LuxuryDestinations", "LuxuryVoyage", "LuxuryTrips", "LuxuryTravelscape", 
        "LuxuryDiscoveries", "LuxuryHoliday", "LuxuryTourism", "LuxuryTravelHub", 
        "LuxuryGetaways", "LuxuryTravelDeals", "LuxuryTourist", "LuxuryRoamersAAAAA"
    ]
    
    results = check_usernames(usernames_to_check)
