import pandas as pd
from bs4 import BeautifulSoup
import re
import requests
import sys

def get_image_url(project_url):
    """
    scrape the media lab website to get the image corresponding to a project

    :param project_url: the url to the project on the media lab website
    :return: the url of the project image if it exists, None otherwise
    """
    try:
        response = requests.get(project_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        hero = soup.find('div', {'class': 'hero'})
        style = hero['style']
    except:
        return
    match = re.search('url\((".+")\)', style)
    if match:
        image_url = match.group(0)[5:-2]
        return image_url

if __name__ == 'main':
    # path to a projects.csv
    in_path = sys.argv[1]
    # path to write the updated csv
    out_path = sys.argv[2]

    df = pd.read_csv(in_path)
    # add a new column
    df['image_url'] = df.apply(lambda x:get_image_url(x['url']), axis=1)
    df.to_csv(out_path)