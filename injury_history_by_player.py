import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_injury_history(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch page. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    injury_section = soup.find('h2', class_='tabellen_ueberschrift', text='Verletzungshistorie')
    if not injury_section:
        print("Injury section not found on the page.")
        return None

    injury_table = injury_section.find_next('table', class_='standard_tabelle')
    if not injury_table:
        print("Injury table not found on the page.")
        return None

    injuries = []
    rows = injury_table.find_all('tr')[1:]  
    for row in rows:
        cols = row.find_all('td')
        if len(cols) == 4:
            season = cols[0].text.strip()
            start_date = cols[1].text.strip()
            end_date = cols[2].text.strip()
            injury_type = cols[3].text.strip()
            injuries.append({
                'Saison': season,
                'von': start_date,
                'bis': end_date,
                'Verletzung': injury_type
            })

    return injuries

if __name__ == "__main__":
    url = "https://www.soccerdonna.de/de/laura-freigang/profil/spieler_13992.html"
    injury_data = scrape_injury_history(url)

    if injury_data:
        df = pd.DataFrame(injury_data)
        df.to_csv("player_injury_history.csv", index=False)
        print("Injury data saved to player_injury_history.csv")
        print(df)
