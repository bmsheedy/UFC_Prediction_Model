"""
---UFC Stats Fighter Web Scraper and Database V1.1---
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
from string import ascii_lowercase
from bs4 import BeautifulSoup
from datetime import date


# Crawls and parses the UFCStats.com for current and former UFC fighters' detailed pages.
def ufcstats_get_fighter_links():

    # Loops through the alphabet (a through z) to get to each page of fighters. Grouped by first initial of last name.
    for i in ascii_lowercase:
        url = 'http://ufcstats.com/statistics/fighters?char=' + i + '&page=all'
        source_code = requests.get(url)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text, 'html.parser')
        index = 1

        # Parses HTML for links to every fighter's detailed page.
        for url in soup.findAll('a', {'class': 'b-link b-link_style_black'}):
            if index % 3 == 0:
                ufcstats_get_fighter_data(url.get('href'))

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
def ufcstats_get_fighter_data(url):

    source_code = requests.get(url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, 'html.parser')
    current_fighter = {}

    # Scraps fighter page for all fight links. Calls ufcstats_get_fight_data with url
    for url in soup.findAll('tr', {'class': 'b-fight-details__table-row b-fight-details__table-row__hover '
                                            'js-fight-details-click'}):
        ufcstats_get_fight_data(url.get('data-link'))

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
            current_fighter["height (ft,in)"] = height_ft_in

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

    fighter_list.append(current_fighter)


# Scraps Fight Data pages for details about fights (Fighters, outcome, etc).
def ufcstats_get_fight_data(url):
    source_code = requests.get(url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, 'html.parser')
    current_fight = {}

    fighter_num = 1
    for name in soup.findAll('a', {'class': 'b-link b-fight-details__person-link'}):
        if fighter_num == 1:
            current_fight["RED Fighter"] = name.string
        else:
            current_fight["BLUE Fighter"] = name.string

        fighter_num += 1

    wl = soup.find('div', {'class': 'b-fight-details__person'})
    wlstring = wl.i.string.strip(' \n')
    if wlstring == 'W':
        current_fight["Winner"] = current_fight["RED Fighter"]
    else:
        current_fight["Winner"] = current_fight["BLUE Fighter"]

    fight_results.append(current_fight)
    print(current_fight)


if __name__ == "__main__":
    start_time = time.time()
    fighter_list = []
    fight_results = []

    ufcstats_get_fighter_links()

    keys = fighter_list[0].keys()
    with open('fighter_data.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(fighter_list)

    keys = fight_results[0].keys()
    with open('fight_data.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(fight_results)

    print(time.time() - start_time)
