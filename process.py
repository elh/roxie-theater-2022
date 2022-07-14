from bs4 import BeautifulSoup
import os
import json
import csv
import re

def open_file(path):
    with open(path, 'rb') as f:
        return f.read()

def save_file(content):
    if not os.path.isdir('output/'):
        os.mkdir('output/')
    with open('output/data.json', 'wb') as f:
        f.write(content)

# TODO: remove title with lowercase that are not actual movie titles. remove qualitifactions like "Phil Tippett's MAD GOD"
# return "" to indicate skip
def format_title(title):
    # punctuation
    title = title.strip().replace('\u2019', '\'')

    # <DIRECTOR>'s <TITLE>
    title = re.sub(r'^[a-zA-Z\s]+\'s ', '', title)

    # common roxie qualifications
    title = re.sub(r' \(.*mm\)', '', title)
    title = re.sub(r' \(.*MM\)', '', title)
    title = re.sub(r' \(.*Restoration\)', '', title)
    title = re.sub(r' \(.*RESTORATION\)', '', title)
    title = re.sub(r'^.*Presents: ', '', title)
    title = re.sub(r'^.*Festival: ', '', title)
    title = re.sub(r'^.*Transmissions: ', '', title)
    title = re.sub(r'^.*Double Feature: ', '', title)
    title = re.sub(r' – Co-Presented .*$', '', title)
    title = re.sub(r'^STAFF PICK: ', '', title)
    title = re.sub(r'^Staff Pick: ', '', title)
    title = re.sub(r'^.*Movie Pick: ', '', title)
    title = re.sub(r'^Sing-Along: ', '', title)
    title = re.sub(r'w/.*$', '', title)
    
    title = re.sub(r' \(\d*\)', '', title)

    # NOTE: titles being lower case is not a general enough rule to omit titles. Older Roxie listings did not use that all caps convention.
    return title

def process_file(path):
    html = open_file(path)

    # data
    movies = {}             # title to {title: text, times: list of date text, link: link to website}
    movies_in_order = []    # titles in order of first appearance

    # parsing
    soup = BeautifulSoup(html, 'html.parser')

    month = soup.find(class_="ai1ec-calendar-title")
    month_text = month.text.split(' ')[0]

    days = soup.find_all(class_="ai1ec-day")

    for day in days:
        date = day.findChild("div", { "class" : "ai1ec-date" }, recursive=True)

        elements = day.findChildren("tr" , recursive=True)

        title_text = ""
        for element in elements:
            title = element.findChild("div", { "class" : "roxie-showtimes-month" }, recursive=True)
            if title:
                # text formatting
                title_text = format_title(title.contents[0].text)
                if not title_text:
                    continue

                # data
                if title_text not in movies:
                    movies[title_text] = {
                        'title': title_text,
                        'link': title.findChild("a", recursive=True).get('href'),
                        'times': [],
                    }
                    movies_in_order.append(title_text)
            else:
                times = element.findChildren("div", { "class" : "now-playing-times-month" }, recursive=True)
                for time in times:
                    time_text = time.text.strip()

                    # data
                    if not title_text:
                        # do not error. we might be intentionally skipping titles
                        continue
                    movies[title_text]['times'].append(month_text + " " + date.text + " " + time_text)

    return {
        'movies': movies,
        'movies_in_order': movies_in_order,
    }

# python process.py
def main():
    all_data = {
        'movies': {},
        'movies_in_order': [],
    }

    data_dir = 'fetch_data'
    for filename in sorted(os.listdir(data_dir)):
        print('processing', filename)
        f = os.path.join(data_dir, filename)
        data = process_file(f)
        
        for m in data['movies']:
            if m not in all_data['movies']:
                all_data['movies'][m] = data['movies'][m]
            else:
                all_data['movies'][m]['times'].extend(data['movies'][m]['times'])
        for m in data['movies_in_order']:
            if m not in all_data['movies_in_order']:
                all_data['movies_in_order'].append(m)

    # json
    all_data_json = json.dumps(all_data, indent=2)
    save_file(bytes(str(all_data_json), 'utf-8'))

    # letterboxd csv
    with open('output/letterboxd.csv', 'w', newline='') as csvfile:
        fieldnames = ['Title', 'Review']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for movie in all_data['movies_in_order']:
            r = all_data['movies'][movie]['link'] + "\n\n"
            if len(all_data['movies'][movie]['times']) == 1:
                r += "1 showing"
            else:
                r += str(len(all_data['movies'][movie]['times'])) + " showings"
            writer.writerow({
                'Title': movie,
                'Review': r,
            })

if __name__ == "__main__":
    main()
