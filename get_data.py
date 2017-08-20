import os

import pandas as pd
import requests
import datetime


def soupify(session, url):
    from bs4 import BeautifulSoup

    tor_proxies = {
        'http': 'socks5://localhost:9050',
        'https': 'socks5://localhost:9050'
    }

    base_page = session.get(url, proxies=tor_proxies)
    soup = BeautifulSoup(base_page.content, 'html.parser')

    return base_page.content, soup


def main():
    url = 'http://fantasy.sofoot.com/?tpl=score'
    LOGIN_URL = 'http://fantasy.sofoot.com/login.php'
    payload = {
        'email': os.environ.get('SFL_EMAIL'),
        'password': os.environ.get('SFL_PWD'),
        'remember': '1'  # remember me
    }

    with requests.Session() as s:
        p = s.post(LOGIN_URL, data=payload)
        # print the html returned or something more intelligent to see if it's a successful login page.
        print(p.text)

        # An authorised request.
        html_content, soup = soupify(s, url)

        title = soup.select('h3')[0].text.strip()

    scores = pd.read_html(html_content)[0]
    scores = scores.drop(scores.index[len(scores)-1])
    scores[['Position', 'Points SFL', "Joueurs l'ayant choisi"]] = scores[['Position', 'Points SFL', "Joueurs l'ayant choisi"]].astype(int)
    total_choice = pd.Series(scores.groupby('Match')["Joueurs l'ayant choisi"].sum(), name='total_choice')
    scores = scores.join(total_choice, on='Match')
    scores["choix_autre"] = scores['total_choice'] - scores["Joueurs l'ayant choisi"]

    scores['bet_safety'] = scores["Joueurs l'ayant choisi"] / (1 + scores["choix_autre"])

    date_element = datetime.date.today().strftime("%Y%m%d")
    scores.to_csv('data/sfl_data_{}.csv'.format(date_element))


if __name__ == '__main__':
    main()

