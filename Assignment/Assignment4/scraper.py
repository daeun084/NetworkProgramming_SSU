import csv
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests


def verify_request(url):
    # check that the url is valid
    try:
        parsed_url = urlparse(url)
        # Check if the url has the correct path
        return (parsed_url.scheme == 'https' and
                parsed_url.netloc == 'en.wikipedia.org' and
                parsed_url.path.startswith('/wiki/'))
    except Exception as e:
        return False


def scrap(url):
    # scrap url's title, first paragraph
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    title = soup.find('h1', {'id': 'firstHeading'}).text.strip()
    # find content text
    content_text = soup.find('div', {'id': 'mw-content-text'})
    # get all p in context text
    paragraphs = content_text.find_all('p')
    # get second p text
    first_paragraph = paragraphs[1].text.strip() if len(paragraphs) > 1 else 'No second paragraph found.'

    return title, first_paragraph


def save_to_csv(title, first_paragraph, filename='Wikipedia_Content.csv'):
    # save title, first paragraph data in csv file
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        # get writer
        writer = csv.writer(file)
        # write row as title, first paragraph
        writer.writerow(['Title', 'First Paragraph'])
        writer.writerow([title, first_paragraph])


if __name__ == '__main__':
    while True:
        # get url from user
        url = input("Wikipedia URL: ")
        if verify_request(url) :
            # if url is valid, break loop
            break
        else :
            # if user enter invalid url, print error message
            print("Invalid URL! Plase Enter Valid URL Again.")

    # get url's information
    title, first_paragraph = scrap(url)
    # save data in csv file
    save_to_csv(title, first_paragraph)

    # print scraped output
    print("\nScraped Output:")
    print(f"Title: {title}")
    print(f"Description: {first_paragraph}")

