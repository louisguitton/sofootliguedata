import os
import datetime

import pandas as pd
import scrapy

BASE_URL = 'http://fantasy.sofoot.com'
USER_NAME = os.environ.get('SFL_EMAIL')
PASSWORD = os.environ.get('SFL_PWD')


class LigueSpider(scrapy.Spider):
    name = "ligue"
    start_urls = [BASE_URL + '/login.php']

    def parse(self, response):
        yield scrapy.FormRequest.from_response(
            response,
            formxpath='//form',
            formdata={
                'email': USER_NAME,
                'password': PASSWORD,
                'remember':'1',
            },
            callback=self.after_login)

    def after_login(self, response):
        base_url = BASE_URL + '/?tpl=score'
        yield scrapy.Request(url=base_url, callback=self.action)

    def action(self, response):

        html_content = response.body
        scores = self.get_scores_from_html(html_content)
        self.save_scores_to_file(scores)

    @staticmethod
    def get_scores_from_html(html_content):
        scores = pd.read_html(html_content)[0]
        scores = scores.drop(scores.index[len(scores) - 1])
        scores[['Position', 'Points SFL', "Joueurs l'ayant choisi"]] = scores[
            ['Position', 'Points SFL', "Joueurs l'ayant choisi"]].astype(int)
        total_choice = pd.Series(scores.groupby('Match')["Joueurs l'ayant choisi"].sum(), name='total_choice')
        scores = scores.join(total_choice, on='Match')
        scores["choix_autre"] = scores['total_choice'] - scores["Joueurs l'ayant choisi"]

        scores['bet_safety'] = scores["Joueurs l'ayant choisi"] / (1 + scores["choix_autre"])
        return scores

    @staticmethod
    def save_scores_to_file(scores):
        date_element = datetime.date.today().strftime("%Y%m%d")
        scores.to_csv(os.path.abspath('data/sfl_data_{}.csv'.format(date_element)))