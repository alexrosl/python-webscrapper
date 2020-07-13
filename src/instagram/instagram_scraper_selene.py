import argparse
from datetime import datetime

import pandas
from selene import be
from selene import browser
from selenium import webdriver

import src.instagram.constants as constants
from src.db.db_utils import DbUtil, InstagramPost
from src.instagram.pages.LoginPage import LoginPage
from src.instagram.pages.UserPage import UserPage


class InstagramSeleneScraper(object):
    def __init__(self, insta_login_user, insta_password, remote_selenide_url):
        self.login_user = insta_login_user
        self.login_password = insta_password
        self.remote_selenide_url = remote_selenide_url

    def setup_module(self):
        driver = webdriver.Remote(
            command_executor=self.remote_selenide_url
            ,
            desired_capabilities={'browserName': 'chrome',
                                  'javascriptEnabled': True}
        )
        browser.set_driver(driver)

    def authenticate_with_login(self):
        secure_page = LoginPage()\
            .open()\
            .login_as(self.login_user, self.login_password)
        secure_page.avatar.should(be.existing)

    def get_profile_info(self, username):
        resp = UserPage().get_body(username)
        user_info = resp['graphql']['user']
        profile_info = {
            'biography': user_info['biography'],
            'followers_count': user_info['edge_followed_by']['count'],
            'following_count': user_info['edge_follow']['count'],
            'full_name': user_info['full_name'],
            'id': user_info['id'],
            'posts': user_info['edge_owner_to_timeline_media']
        }
        return profile_info

    def get_posts(self, usernames: list):
        posts = []
        for username in usernames:
            profile_info = self.get_profile_info(username)
            posts_edges = profile_info['posts']['edges']
            for post_edge in posts_edges:
                d = {}
                d['insta_id'] = post_edge['node']['id']
                d['author'] = post_edge['node']['owner']['username']
                try:
                    d['text'] = post_edge['node']['edge_media_to_caption']['edges'][0]['node']['text']
                except:
                    d['text'] = None
                d['link'] = constants.BASE_URL + "p/" + post_edge['node']['shortcode']
                timestamp = post_edge['node']['taken_at_timestamp']
                d['datetime'] = datetime.utcfromtimestamp(timestamp)
                posts.append(d)
        return posts


def main(usernames, insta_login_user, insta_password, remote_selenide_url):
    instagram_scraper = InstagramSeleneScraper(insta_login_user, insta_password, remote_selenide_url)
    instagram_scraper.setup_module()
    instagram_scraper.authenticate_with_login()
    posts = instagram_scraper.get_posts(usernames)

    pandas.set_option('display.max_colwidth', None)
    df = pandas.DataFrame(posts)
    # df = df.sort_values(by=['datetime'], ascending=False)

    # df.to_csv("insta_posts.csv", header=True, columns=columns)

    db_util = DbUtil()
    for index, row in df.iterrows():
        insta_post = InstagramPost(
            insta_id=row.at["insta_id"],
            link=row.at["link"],
            author=row.at["author"],
            text=row.at["text"],
            datetime=row.at["datetime"])
        db_row = db_util.read(InstagramPost).filter(InstagramPost.insta_id == row.at["insta_id"])
        db_util.upsert(db_row, insta_post, InstagramPost.__tablename__)


if __name__ == '__main__':
    CLI = argparse.ArgumentParser()
    CLI.add_argument(
        "--insta_usernames",  # name on the CLI - drop the `--` for positional/required parameters
        nargs="*",  # 0 or more values expected => creates a list
        type=str
    )
    CLI.add_argument(
        "--insta_login_user",  # name on the CLI - drop the `--` for positional/required parameters
        nargs="*",  # 0 or more values expected => creates a list
        type=str
    )
    CLI.add_argument(
        "--insta_password",  # name on the CLI - drop the `--` for positional/required parameters
        nargs="*",  # 0 or more values expected => creates a list
        type=str
    )
    CLI.add_argument(
        "--insta_selenide_url",  # name on the CLI - drop the `--` for positional/required parameters
        nargs="*",  # 0 or more values expected => creates a list
        type=str
    )
    args, unknown = CLI.parse_known_args()
    main(args.insta_usernames, args.insta_login_user[0], args.insta_password[0], args.insta_selenide_url[0])