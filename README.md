# roxie-theater

Simple scripts for fetching showtimes from the [Roxie Theater](https://www.roxie.com/) website and processing them. The initial use case was to produce import csv files to populate Letterboxd lists like this: [Roxie Theater 2022 🌉](https://letterboxd.com/eugeually/list/roxie-theater-2022/).

## Usage

### fetch showtimes from roxie.com

```
python fetch.py [-months_before N] [-months_after N]
```

pulls Roxie Theater showings and saves html in `fetch_data/`. `-months_before` and `-months_after` flags are optional and specify how many months to fetch before and after the current month.

### process showtimes into useful formats

```
python process.py
```

processes files in `fetch_data/` and produces `output/data.json` summary and `output/letterboxd.csv` Letterboxd import csv.

see `process.py` `format_title` for some really opinionated, brittle sanitization attempts. These cover a decent amount of cases.

## Setup

`pip install -r requirements.txt`
