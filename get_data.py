from bs4 import BeautifulSoup as bs
import requests
import re

url = 'http://sofifa.com/players?offset=0'


fifa_stats = ['Crossing', 'Finishing', 'Heading Accuracy',
              'Short Passing', 'Volleys', 'Dribbling', 'Curve',
              'Free Kick Accuracy', 'Long Passing', 'Ball Control',
              'Acceleration', 'Sprint Speed', 'Agility', 'Reactions',
              'Balance', 'Shot Power', 'Jumping', 'Stamina', 'Strength',
              'Long Shots', 'Aggression', 'Interceptions', 'Positioning',
              'Vision', 'Penalties', 'Composure', 'Marking', 'Standing Tackle',
              'Sliding Tackle', 'GK Diving', 'GK Handling', 'GK Kicking',
              'GK Positioning', 'GK Reflexes']


def soup_maker(url):
    r = requests.get(url)
    markup = r.content
    soup = bs(markup, 'lxml')
    return soup


def find_top_players(soup):
    raw = []
    table = soup.find('table', {'class': 'table-hover'})
    tbody = table.find('tbody') 
    all_a = tbody.find_all('a', {'class': 'tooltip'}) 
    for player in all_a:
        final_details= {}
        final_details['short_name'] = player.text 
        final_details.update(player_all_details('http://sofifa.com' + player['href']))
        raw.append(final_details)

    return raw


def find_player_info(soup):
    player_data = {}
    player_data['image'] = soup.find('img')['data-src']
    player_data['full_name'] = soup.find('h1').text.split(' (')[0]
    span = soup.find('div', attrs={'class': 'meta bp3-text-overflow-ellipsis'}).text.strip()
    infos = span.split(' ')
    player_data['age'] = infos[3][:-4]
    player_data['height'] = infos[-2] 
    player_data['weight'] = infos[-1]
    div_values = soup.find_all('div', attrs={'class': None}) 
    player_data['Value'] = div_values[-2].text[:-5]
    player_data['Wage'] = div_values[-1].text[:-4]
    # player_data[div_title[2].text] = span_title[1].text
    # player_data[div_title[3].text] = span_title[1].text
    return(player_data )


def find_player_stats(soup):
    player_data = {}
    info = re.findall('\d+', soup.text)
    player_data['rating'] = int(info[0])
    player_data['potential'] = int(info[1])
    player_data['value'] = int(info[2])
    player_data['wage'] = int(info[3])
    return(player_data)


def find_player_secondary_info(soup):
    player_data = {}
    player_data['preff_foot'] = soup.find('label', text='Preferred Foot')\
        .parent.contents[2].strip('\n ')
    player_data['club'] = soup.find_all('ul')[1].find('a').text
    player_data['club_pos'] = soup.find('label', text='Position')\
        .parent.find('span').text
    player_data['club_jersey'] = soup.find('label', text='Jersey number')\
        .parent.contents[2].strip('\n ')
    if soup.find('label', text='Joined'):
        player_data['club_joined'] = soup.find('label', text='Joined')\
            .parent.contents[2].strip('\n ')
    player_data['contract_valid'] = soup.find(
        'label', text='Contract valid until')\
        .parent.contents[2].strip('\n ')
    if len(soup.find_all('ul')) > 2:
        player_data['country'] = soup.find_all('ul')[2].find('a').text
    return(player_data)


def find_fifa_info(soup):
    player_data = {}
    divs_without_skill = soup[1].find_all('div', {'class': 'col-3'})[:3]
    more_lis = [div.find_all('li') for div in divs_without_skill]
    lis = soup[0].find_all('li') + more_lis[0]
    for li in lis:
        for stats in fifa_stats:
            if stats in li.text:
                player_data[stats.replace(' ', '_').lower()] = int(
                    (li.text.split(' ')[0]).replace('\n', ''))
    traits = soup[1].find('h4', text='Traits')
    if traits:
        player_data['traits'] = [li.text.replace('\xa0', '') for li in
            traits.parent.next_sibling.next_sibling.find_all('li')]
    specialities = soup[1].find('h4', text='Specialities')
    if specialities:
        player_data['specialities'] = [li.text.replace('\xa0', '') for li in
            specialities.parent.next_sibling.next_sibling.find_all('li')]
    return(player_data)


def player_all_details(url):
    all_details = {}
    soup = soup_maker(url) 
    player_info = soup.find('div', {'class': 'player'})
    all_details.update(find_player_info(player_info))
    # player_stats = soup.find('div', {'class': 'stats'})
    # print(soup)
    # all_details.update(find_player_stats(player_stats))
    # secondary_info = soup.find('div', {'class': 'teams'})
    # all_details.update(find_player_secondary_info(secondary_info))
    # fifa_info = soup.find_all('div', {'class': 'columns mb-20'})
    # all_details.update(find_fifa_info(fifa_info))
    return(all_details)

import pandas as pd
soup = soup_maker(url)
data = find_top_players(soup)
df = pd.DataFrame(data)
df.to_csv('soccer.csv')