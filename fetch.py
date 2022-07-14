import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import argparse

def save_file(date_obj, content):
    if not os.path.isdir('fetch_data/'):
        os.mkdir('fetch_data/')
    with open(f'fetch_data/{date_obj.strftime("%Y_%m")}_calendar.html', 'wb') as f:
        f.write(content)

# fetch and save a calendar page
# returns the calendar month as a datetime object, page content, link to previous and next months
def fetch(url):
    response = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})

    soup = BeautifulSoup(response.content, 'html.parser')
    month = soup.find(class_="ai1ec-calendar-title")
    month_obj = datetime.strptime(month.text, '%B %Y')

    save_file(month_obj, response.content)

    print('fetched and saved', month_obj.strftime("%B %Y"))
    return {
        'month': month_obj,
        'content': response.content,
        'prev': soup.find(class_="ai1ec-prev-month").get('href'),
        'next': soup.find(class_="ai1ec-next-month").get('href'),
    }

# python fetch.py [-months_before N] [-months_after N]
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-months_before', type=int, default=0)
    parser.add_argument('-months_after', type=int, default=0)
    args = parser.parse_args()

    base_res = fetch("https://www.roxie.com/calendar")

    # -months_after months ahead
    cur = base_res
    for x in range(0, args.months_after):
        if cur['next']:
            cur = fetch(cur['next'])
        else:
            print('no next')
            break
    
    # -months_before months back
    cur = base_res
    for x in range(0, args.months_before):
        if cur['prev']:
            cur = fetch(cur['prev'])
        else:
            print('no prev')
            break

if __name__ == "__main__":
    main()
