import os
import requests
import base64
import bs4

from datetime import date
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

date_obj = date.today()
FILE_NAME = f"/tmp/KindleNews {date_obj.strftime('%m-%d')}.txt"

def send_file_to_kindle(file_name: str) -> int:
    # Given a file name, sends this file to my Kindle
    message = Mail(
        from_email='kindle@doorlay.com',
        to_emails='ndoorlay@kindle.com',
        subject='Convert',
        html_content=" "
    )
    with open(file_name, 'rb') as f:
        data = f.read()
        f.close()
    encoded_file = base64.b64encode(data).decode()
    attachedFile = Attachment(
        FileContent(encoded_file),
        FileName(FILE_NAME[5:]),
        FileType('text/plain'),
        Disposition('attachment')
    )
    message.attachment = attachedFile
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    response = sg.send(message)
    return response.status_code


def scrape_page(url: str) -> requests.models.Response:
    # Given a URL, GETs the page
    page = requests.get(url)
    if page.status_code != 200:
        raise Exception(f"Error grabbing page: {page.status_code}")
    return page


def get_article_links(page: requests.models.Response) -> list:
    # Given a page, extracts a list of all article links
    soup = bs4.BeautifulSoup(page.text, features="html.parser")
    article_divs = soup.find_all("h3", class_="PagePromo-title")
    article_links = []
    for article in article_divs:
        # Prevents trending articles from accidentally being added
        if len(article.a.get("class")) == 1:
            article_links.append(article.a.get("href"))
    return article_links


def parse_page(page: requests.models.Response) -> str:
    # Given a requests response page, returns a string representing an article
    soup = bs4.BeautifulSoup(page.text, features="html.parser")
    split_article = soup.find_all("p")
    # Remove photo descriptions
    new_split_article = []
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
    # Given a string article, determines whether or not it is a valid article
    return not article[0:35] == "Copyright 2024 The Associated Press"


def write_to_outfile(article: str) -> None:
    # Given a string article, writes this to the output .txt file
    out_file = open(FILE_NAME, "a")
    out_file.write(article)
    out_file.write("\n\n")
    out_file.close()


def handler(event, context):
    f = open(FILE_NAME, "x")
    f.close()
    urls = ["https://apnews.com/us-news"]
    for i, url in enumerate(urls):
        page = scrape_page(url)
        article_links = get_article_links(page)
        out_file = open(FILE_NAME, "a")
        if i == 0:
            out_file.write("U.S. NEWS\n\n")
        out_file.close()
        article_set = set()
        for article in article_links:
            page = scrape_page(article)
            article = parse_page(page)
            # Add articles to a set to remove duplicates
            if is_valid_article(article):
                article_set.add(article)
        for article in article_set:
            write_to_outfile(article)
    send_file_to_kindle(FILE_NAME)
            
handler(None, None)