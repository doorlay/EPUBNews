import os
import requests
import base64
import bs4

from datetime import date
from exceptions import FileScrapeException
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

date_obj = date.today()
DEFAULT_FILE_NAME = "Associated Press News.txt"
# DEFAULT_FILE_NAME = f"/tmp/KindleNews {date_obj.strftime('%m-%d')}.txt"

def send_data_to_kindle(file_name: str, file_data: bytes) -> None:
    """Given a file name and raw data, sends this to my Kindle."""
    message = Mail(
        from_email='kindle@doorlay.com',
        to_emails='ndoorlay@kindle.com',
        subject='Convert',
        html_content=" "
    )
    encoded_file = base64.b64encode(file_data).decode()
    attachedFile = Attachment(
        FileContent(encoded_file),
        FileName(file_name),
        FileType('text/plain'),
        Disposition('attachment')
    )
    message.attachment = attachedFile
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    sg.send(message)


def convert_to_bytes(file_name: str) -> bytes:
    """Given a file name, returns the file contents in bytes."""
    with open(file_name, "rb") as file_obj:
        data = file_obj.read()
    return data


def scrape_page(url: str) -> requests.models.Response:
    """Given a URL, scrapes the page and returns a requests.models.Response object."""
    page = requests.get(url)
    if page.status_code != 200:
        raise FileScrapeException(f"Error grabbing page: {page.status_code}")
    return page


def get_article_links(page: requests.models.Response) -> list:
    """Given a requests.models.Response object, returns a list of links to articles."""
    soup = bs4.BeautifulSoup(page.text, features="html.parser")
    article_divs = soup.find_all("h3", class_="PagePromo-title")
    article_links = []
    for article in article_divs:
        # Prevents trending articles from accidentally being added
        if len(article.a.get("class")) == 1:
            article_links.append(article.a.get("href"))
    return article_links


def parse_page(page: requests.models.Response) -> str:
    """Given a requests.models.Response object, parses a page and returns a string representation of the article."""
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
    """Given an article, determines whether or not it is valid. This is a bit hacky but gets the job done."""
    return not article[0:35] == "Copyright 2024 The Associated Press"


def write_to_outfile(article: str, outfile_name: str) -> None:
    """Given an article as a string and a file object, write the article to thefile object."""
    with open(outfile_name, "a") as file_obj:
        file_obj.write(article)
        file_obj.write("\n\n")


def handler(event, context):
    # Write to a local file (instead of sending to Kindle) if "test_file" is present in the event
    if "test" in event:
        file_name = f"tests/{event['test']}"
    else:
        file_name = DEFAULT_FILE_NAME
    with open(file_name, "w"):
        pass

    urls = ["https://apnews.com/us-news"]
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
    
    if "test" not in event:
        file_data = convert_to_bytes(file_name)
        send_data_to_kindle(file_name, file_data)

