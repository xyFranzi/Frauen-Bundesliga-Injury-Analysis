import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# 添加请求头 
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.soccerdonna.de/',
    'Connection': 'keep-alive',
}

def fetch_player_injury_history(player_url, team_name):
    # response = requests.get(player_url)
    # if response.status_code != 200:
    #     print(f"Failed to fetch player page: {player_url}")
    #     return []
    try:
        # 使用 headers 模拟浏览器请求
        response = requests.get(player_url, headers=HEADERS, timeout=10)
        response.raise_for_status()  # 确保状态码为 200
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch player page: {player_url}, Error: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate "Verletzungshistorie" table
    injury_section = soup.find('h2', class_='tabellen_ueberschrift', string='Verletzungshistorie')
    injury_table = injury_section.find_next('table', class_='standard_tabelle') if injury_section else None

    # Extract player name
    player_name = soup.find('h1', style='color:#fff;').text.strip() if soup.find('h1', style='color:#fff;') else "Unknown"

    player_age = "Unknown"
    # Locate the row containing "Alter"
    age_row = soup.find('td', text='Alter:')
    if age_row:
        age_td = age_row.find_next_sibling('td') 
        if age_td:
            player_age = age_td.text.strip()

    player_height = "Unknown"
    # Locate the row containing "Grösse"
    height_row = soup.find('td', text='Grösse:')
    if height_row:
        height_td = height_row.find_next_sibling('td')  
        if height_td:
            player_height = height_td.text.strip()

    player_nationality = "Unknown"
    # Locate the row containing "Nationalität"
    nationality_row = soup.find('td', text='Nationalität:')
    if nationality_row:
        nationality_td = nationality_row.find_next_sibling('td')  # Get the sibling <td> 
        if nationality_td:
            player_nationality = nationality_td.text.strip()

    player_position = "Unknown"
    # Locate the row containing "Position"
    position_row = soup.find('td', text='Position:')
    if position_row:
        position_td = position_row.find_next_sibling('td')  
        if position_td:
            player_position = position_td.text.strip()

    player_value = "Unknown"
    # Locate the row containing "Marktwert"
    value_row = soup.find('td', text='Marktwert:')
    if value_row:
        value_td = value_row.find_next_sibling('td')  
        if value_td:
            player_value = value_td.text.strip()

    injuries = []
    if injury_table:
        rows = injury_table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 4:
                season = cols[0].text.strip()
                start_date = cols[1].text.strip()
                end_date = cols[2].text.strip()
                injury_type = cols[3].text.strip()
                injuries.append({
                    'Player Name': player_name,
                    'Team Name': team_name,
                    'Age': player_age,
                    'Height':player_height,
                    'Position':player_position,
                    'Value':player_value,
                    'Saison': season,
                    'von': start_date,
                    'bis': end_date,
                    'Verletzung': injury_type
                })
    else:
        # No injury information found
        injuries.append({
            'Player Name': player_name,
            'Team Name': team_name,
            'Age': player_age,
            'Height':player_height,
            'Position':player_position,
            'Value':player_value,
            'Saison': "00/00",
            'von': "00.00.0000",
            'bis': "00.00.0000",
            'Verletzung': "No injury info"
        })
    
    return injuries

def scrape_team_players(base_url, team_url, team_name):
    # response = requests.get(team_url)
    # if response.status_code != 200:
    #     print(f"Failed to fetch team page: {team_url}")
    #     return []
    try:
        # 使用 headers 模拟浏览器请求
        response = requests.get(team_url, headers=HEADERS, timeout=10)
        response.raise_for_status()  # 确保状态码为 200
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch team page: {team_url}, Error: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate player URLs in the team roster
    player_links = []
    player_table = soup.find('table', id='spieler')
    if player_table:
        for link in player_table.find_all('a', href=True):
            if '/profil/spieler_' in link['href']:
                player_links.append(base_url + link['href'])

    print(f"Found {len(player_links)} players in the team: {team_url}")

    all_injuries = []
    for player_url in player_links:
        print(f"Fetching injury history for player: {player_url}")
        player_injuries = fetch_player_injury_history(player_url, team_name)
        for injury in player_injuries:
            injury['Player URL'] = player_url
        all_injuries.extend(player_injuries)

        print(all_injuries[2:])

        # Add random delay to avoid being blocked
        time.sleep(random.uniform(2, 5))

    return all_injuries

def scrape_league_teams(base_url, league_url):
    # response = requests.get(league_url)
    # if response.status_code != 200:
    #     print(f"Failed to fetch league page: {league_url}")
    #     return []
    try:
        # 使用 headers 模拟浏览器请求 (修改 4)
        response = requests.get(league_url, headers=HEADERS, timeout=10)
        response.raise_for_status()  # 确保状态码为 200
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch league page: {league_url}, Error: {e}")
        return []
        
    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate team URLs in the league page
    team_links = []
    team_table = soup.find('table', class_='standard_tabelle')
    if team_table:
        for link in team_table.find_all('a', href=True):
            if '/startseite/verein_' in link['href']:
                team_url = base_url + link['href']
                team_name = link.text.strip()
                
                # Only add if team_name is not empty
                if team_name and (team_url, team_name) not in team_links:
                    team_links.append((team_url, team_name))

    # Print extracted teams
    print("Extracted team links and names:")
    for team_url, team_name in team_links:
        print(f"Team URL: {team_url}, Team Name: {team_name}")

    print(f"Found {len(team_links)} teams in the league.")

    # visited_teams = set()  # 用来记录已经抓取过的球队
    all_injuries = []
    for team_url, team_name in team_links:
        # if team_name in visited_teams:  # 如果球队 URL 已经处理过，跳过
        #     print(f"Skipping already visited team: {team_name}")
        #     continue
        # visited_teams.add(team_name)  # 标记球队为已处理

        print(f"Fetching players from team: {team_name}")
        team_injuries = scrape_team_players(base_url, team_url, team_name)
        all_injuries.extend(team_injuries)

    return all_injuries

if __name__ == "__main__":
    base_url = "https://www.soccerdonna.de"
    league_url = "https://www.soccerdonna.de/de/bundesliga/startseite/wettbewerb_BL1.html"

    injuries = scrape_league_teams(base_url, league_url)

    if injuries:
        df = pd.DataFrame(injuries)
        df.to_csv("league_player_injury_history.csv", index=False)
        print("Injury history saved to league_player_injury_history.csv")
        print(df)
