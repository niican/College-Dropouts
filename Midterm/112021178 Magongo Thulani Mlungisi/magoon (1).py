import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}  # Example User-Agent

def scrape_github():
    url = 'https://github.com/trending/developers'
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            devs = soup.find_all('h1', class_='h3 lh-condensed')
            for dev in devs:
                link_tag = dev.find('a', class_='Link')


                href_value = link_tag['href']
                print(href_value)
    except:
        pass
scrape_github()