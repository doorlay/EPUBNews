import os
import requests
import base64
import bs4
import json

from dotenv import load_dotenv
from time import sleep
from datetime import date
from constants import FEED_TO_URL
from exceptions import FileScrapingException

date_obj = date.today()
DEFAULT_FILE_NAME = f"EPUB News {date_obj}.txt"


def get_urls():
    """Get the URLs from which to scrape news."""
    load_dotenv()
    urls = []
    for key, value in os.environ.items():
        # Process Associated Process env vars
        if "ASSOCIATED_PRESS" in key:
            if value == "ENABLED":
                url = FEED_TO_URL[key]
                urls.append(url)
    return urls
    

def convert_to_bytes(file_name: str) -> bytes:
    """Given a file name, returns the file contents in bytes."""
    with open(file_name, "rb") as file_obj:
        data = file_obj.read()
    return data


def scrape_page(url: str) -> requests.models.Response:
    """Scrape a page and return a Response object."""
    page = requests.get(url)
    if page.status_code != 200:
        raise FileScrapingException(f"Error grabbing page: {page.status_code}")
    return page


def get_article_links(page: requests.models.Response) -> list:
    """Given a Response object, returns a list of links to articles."""
    soup = bs4.BeautifulSoup(page.text, features="html.parser")
    article_divs = soup.find_all("h3", class_="PagePromo-title")
    article_links = []
    for article in article_divs:
        # Prevents trending articles from accidentally being added
        if len(article.a.get("class")) == 1:
            article_links.append(article.a.get("href"))
    return article_links


def parse_page(page: requests.models.Response) -> str:
    """Given a Response object, parse a page and return a string representation of the article."""
    soup = bs4.BeautifulSoup(page.text, features="html.parser")
    split_article = soup.find_all("p")
    new_split_article = []

    # Prevent photo descriptions from making their way into the final product
    for p_tag in split_article:
        if "(AP Photo" not in p_tag.get_text() and "via AP)" not in p_tag.get_text():
            new_split_article.append(p_tag)
    first_ptag = 0
    for i, p_tag in enumerate(new_split_article):
        if "(AP) — " in p_tag.get_text():
            first_ptag = i

    # Removes paragraph tags, cuts out pre-article
    article = " ".join([str(p_tag).replace("<p>","").replace("</p>","") for p_tag in new_split_article[first_ptag:-1]])

    # Removes all <span> and <a> tags, extracts their content
    soup = bs4.BeautifulSoup(article, features="html.parser")
    article = soup.get_text()
    return article


def is_valid_article(article: str) -> bool:
    """Determines whether a string article is valid."""
    # TODO: Figure out if there is a less hacky way to do this. Reliance on the copyright year is not good!
    return not article[0:35] == "Copyright 2024 The Associated Press"


def write_to_outfile(article: str, outfile_name: str) -> None:
    """Given an article as a string and a file object, write the article to thefile object."""
    with open(outfile_name, "a") as file_obj:
        file_obj.write(article)
        file_obj.write("\n\n")


file_name = DEFAULT_FILE_NAME
with open(file_name, "w"):
    pass
urls = get_urls()
for url in urls:
    page = scrape_page(url)
    article_links = get_article_links(page)
    article_set = set()
    for article in article_links:
        page = scrape_page(article)
        article = parse_page(page)
        # Add articles to a set to remove duplicates
        if is_valid_article(article):
            article_set.add(article)

    with open(file_name, "a") as file_obj:
        file_obj.write("U.S. NEWS\n\n")

    for article in article_set:
        write_to_outfile(article, file_name)
