"""
---UFC Fighter Web Scraper and Database---
-----------------------------------------------------------------------------------------------------------------------
Crawls and parses multiple websites for raw data and statistics.
Along with the standard statistics, the database includes advanced metrics computed from the raw data.
This database is used by Brandon's UFC Machine Learning Model to predict fight outcomes.
-----------------------------------------------------------------------------------------------------------------------
---Created by Brandon Sheedy---
"""

import time
import aiohttp
import asyncio
from string import ascii_lowercase
from bs4 import BeautifulSoup

page_urls = []
fighter_urls = []
fighter_list = []


# Loops through the alphabet (a through z) to get to each page of fighters. Grouped by first initial of last name.
def ufcstats_get_pages():
    for i in ascii_lowercase:
        url = 'http://ufcstats.com/statistics/fighters?char=' + i + '&page=all'
        page_urls.append(url)


async def ufcstats_get_fighter_links(session, url):

    async with session.get(url) as response:
        plain_text = await response.text()
        soup = BeautifulSoup(plain_text, 'html.parser')
        index = 1

        # Parses HTML for links to every fighter's detailed page.
        for link in soup.findAll('a', {'class': 'b-link b-link_style_black'}):
            if index % 3 == 0:
                fighter_urls.append(link.get('href'))

            index += 1


# Scraps data from a fighters' detailed pages found in the ufcstats_get_links function.
async def ufcstats_get_data(session, url):

    async with session.get(url) as response:
        plain_text = await response.text()
        soup = BeautifulSoup(plain_text, 'html.parser')
        current_fighter = {}

        # Scraps fighter page for their name.
        for name in soup.findAll('span', {'class': 'b-content__title-highlight'}):
            current_fighter["name"] = name.string.strip("\n ")

        # Scraps fighter page for their height.
        item_num = 1
        for item in soup.findAll('li', {'class': 'b-list__box-list-item b-list__box-list-item_type_block'}):
            if item_num == 1:
                current_fighter["height"] = item.text.strip("Height:\n ")

            item_num += 1

        fighter_list.append(current_fighter)
        print(len(fighter_list))


async def main():
    ufcstats_get_pages()

    tasks = []
    
    async with aiohttp.ClientSession() as session:
        for url in page_urls:
            tasks.append(ufcstats_get_fighter_links(session, url))

        for task in tasks:
            await task

        tasks.clear()

        for url in fighter_urls:
            tasks.append(ufcstats_get_data(session, url))

        for task in tasks:
            await task

        print(fighter_list)
        print(time.time() - start_time)


if __name__ == "__main__":
    start_time = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

