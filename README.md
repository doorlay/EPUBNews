# Overview
A simple program to scrape news articles and format them as .epubs. This currently supports only Associated Press news (as that's what I read), but open to PRs for other news sites as well. I have this running as a CRON job and sending to my Kindle each morning, for those looking for inspiration.

## Setup
1. Run the following:
```
python3 -m venv .venv
source .venv/bin/activate
pip install .
cp .env.sample .env
```
2. Within your new `.env` file, mark each news feed as either "enabled" or "disabled" as appropriate.

## Usage
1. Run the script with `python3 epub_news.py`.