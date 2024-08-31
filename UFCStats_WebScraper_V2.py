"""
---UFC Stats Fighter Web Scraper and Database V1.2---
-----------------------------------------------------------------------------------------------------------------------
Crawls and parses multiple websites for raw data and statistics.
Along with the standard statistics, the database includes advanced metrics computed from the raw data.
This database is used by Brandon's UFC Machine Learning Model to predict fight outcomes.
-----------------------------------------------------------------------------------------------------------------------
---Created by Brandon Sheedy---
"""
import requests
import time
import re
import csv
import concurrent.futures
from string import ascii_lowercase
from bs4 import BeautifulSoup
from datetime import date


def get_data(letter_url):
    response = requests.get(letter_url)
    plain_text = response.text
    soup = BeautifulSoup(plain_text, 'html.parser')

    index = 1

    # Parses HTML for links to every fighter's detailed page.
    for f_url in soup.findAll('a', {'class': 'b-link b-link_style_black'}):
        if index % 3 == 0:
            get_fighter_data(f_url.get('href'))

        index += 1


# Calculates the fighter's age from their date of birth.
def age(dob):
    today = date.today()

    month_text = dob[0:3]
    if month_text == 'Jan':
        month_num = 1
    elif month_text == 'Feb':
        month_num = 2
    elif month_text == 'Mar':
        month_num = 3
    elif month_text == 'Apr':
        month_num = 4
    elif month_text == 'May':
        month_num = 5
    elif month_text == 'Jun':
        month_num = 6
    elif month_text == 'Jul':
        month_num = 7
    elif month_text == 'Aug':
        month_num = 8
    elif month_text == 'Sep':
        month_num = 9
    elif month_text == 'Oct':
        month_num = 10
    elif month_text == 'Nov':
        month_num = 11
    else:
        month_num = 12

    day_num = int(dob[4:6])
    year_num = int(dob[8:13])

    b = date(year_num, month_num, day_num)
    return today.year - b.year - ((today.month, today.day) < (b.month, b.day))


# Scraps data from a fighters' detailed pages found in the ufcstats_get_links function.
def get_fighter_data(url):
    response = requests.get(url)
    plain_text = response.text
    soup = BeautifulSoup(plain_text, 'html.parser')
    current_fighter = {}

    # Scraps fighter page for all fight links. Calls ufcstats_get_fight_data with url
    for url in soup.findAll('tr', {'class': 'b-fight-details__table-row b-fight-details__table-row__hover '
                                            'js-fight-details-click'}):
        params = []
        for x in url.findAll('a', {'class': 'b-link b-link_style_black'}):
            params.append(x.string.strip(' \n'))

        fight_pulled = False
        for f in fight_data:
            if f["Event"] == params[2] and (f["RED Fighter"] == params[0] or f["RED Fighter"] == params[1]):
                fight_pulled = True
                break

        if not fight_pulled:
            get_fight_data(url.get('data-link'))

    # Scraps fighter page for their name.
    for name in soup.findAll('span', {'class': 'b-content__title-highlight'}):
        current_fighter["name"] = name.string.strip("\n ")

    # Scraps fighter page for their nickname.
    for nickname in soup.findAll('p', {'class': 'b-content__Nickname'}):
        current_fighter["nickname"] = nickname.string.strip("\n ")

    # Scraps fighter page for measurables and career stats on UFCstat.com based on the item_num in the loop.
    # 1 = height, 2 = weight, 3 = reach, 4 = stance, 5 = DOB, 6 = SLpM, 7 = str. acc., 8 = SApM, 9 = str. def.,
    # 10 is unused, 11 = td avg, 12 = td acc., 13 = td def., 14 = sub. avg.
    item_num = 1
    for item in soup.findAll('li', {'class': 'b-list__box-list-item b-list__box-list-item_type_block'}):

        if item_num == 1:
            height_ft_in = item.text.strip("Height:\n ")

            # Converts height to just inches, if a height was found.
            if height_ft_in != '--':
                pattern = "[0-9]+?[0-9]*"
                ft_in = re.findall(pattern, height_ft_in)
                height_in = int(ft_in[0])*12 + int(ft_in[1])
                current_fighter["height (in)"] = height_in
            else:
                current_fighter["height (in)"] = height_ft_in
        elif item_num == 2:
            weight_lbs = item.text.strip("Weight:\n lbs.")
            if weight_lbs != '--':
                weight_lbs = int(weight_lbs)
            current_fighter["weight (lbs)"] = weight_lbs
        elif item_num == 3:
            reach = item.text.strip("Reach:\n \"")
            if reach != '--':
                reach = int(reach)
            current_fighter["reach (in)"] = reach
        elif item_num == 4:
            stance = item.text.strip("STANCE:\n ")
            if stance == 'witch':
                stance = 'Switch'
            elif stance == 'outhpaw':
                stance = 'Southpaw'
            elif stance == 'ideways':
                stance = 'Sideways'
            current_fighter["stance"] = stance
        elif item_num == 5:
            dob = item.text.strip("\n ").strip("DOB:").strip("\n ")
            current_fighter["DOB"] = dob
            if dob != '--':
                fighter_age = age(dob)
            else:
                fighter_age = '--'
            current_fighter["age"] = fighter_age
        elif item_num == 6:
            slpm = float(item.text.strip("SLpM:\n "))
            current_fighter["Sig. Strikes Landed per min."] = slpm
        elif item_num == 7:
            str_acc = int(item.text.strip("Str. Acc.:\n%"))
            current_fighter["Striking Accuracy (%)"] = str_acc
        elif item_num == 8:
            sapm = float(item.text.strip("SApM:\n "))
            current_fighter["Sig. Strikes Absorbed per min."] = sapm
        elif item_num == 9:
            str_def = int(item.text.strip("Str. Def:\n%"))
            current_fighter["Striking Defense (%)"] = str_def
        elif item_num == 11:
            td_avg = float(item.text.strip("TD Avg.:\n "))
            current_fighter["TD Avg. per 15 min"] = td_avg
        elif item_num == 12:
            td_acc = int(item.text.strip("TD. Acc.:\n%"))
            current_fighter["Takedown Accuracy (%)"] = td_acc
        elif item_num == 13:
            td_def = int(item.text.strip("TD. Def.:\n%"))
            current_fighter["Takedown Defense (%)"] = td_def
        elif item_num == 14:
            sub_avg = float(item.text.strip("Sub. Avg.:\n"))
            current_fighter["Sub. Attempt Avg. per 15 min (%)"] = sub_avg

        item_num += 1

    fighter_data.append(current_fighter)


# Scraps Fight Data pages for details about fights (Fighters, outcome, etc).
def get_fight_data(url):
    response = requests.get(url)
    plain_text = response.text
    soup = BeautifulSoup(plain_text, 'html.parser')
    current_fight = {}

    for event in soup.find('a', {'class': 'b-link'}):
        current_fight["Event"] = event.string.strip(' \n')

    index = 1
    for name in soup.findAll('a', {'class': 'b-link b-fight-details__person-link'}):
        if index == 1:
            current_fight["RED Fighter"] = name.string.strip(' \n')
        else:
            current_fight["BLUE Fighter"] = name.string.strip(' \n')

        index += 1

    wl = soup.find('div', {'class': 'b-fight-details__person'})
    wl_string = wl.i.string.strip(' \n')
    if wl_string == 'W':
        current_fight["Winner"] = current_fight["RED Fighter"]
    else:
        current_fight["Winner"] = current_fight["BLUE Fighter"]

    fight_data.append(current_fight)


if __name__ == "__main__":
    start_time = time.time()

    page_urls = []
    fighter_data = []
    fight_data = []

    for i in ascii_lowercase:
        http = 'http://ufcstats.com/statistics/fighters?char=' + i + '&page=all'
        page_urls.append(http)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(get_data, page_urls)

    keys = fighter_data[0].keys()
    with open('fighter_data.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(fighter_data)

    keys = fight_data[0].keys()
    with open('fight_data.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(fight_data)

    print(time.time() - start_time)
