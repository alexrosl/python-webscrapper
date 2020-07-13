import argparse
import json
import logging
from datetime import datetime

import pandas
import requests

import src.instagram.constants as constants
from src.db.db_utils import DbUtil, InstagramPost


class InstagramSimpleScrapper(object):
    def __init__(self, login_user, login_password):
        self.session = requests.Session()
        self.session.headers = {'user-agent': constants.CHROME_LINUX_UA}
        self.login_user = login_user
        self.login_pass = login_password
        self.logger = logging.getLogger(__name__)

    def authenticate_as_guest(self):
        """Authenticate as a guest/non-signed in user"""
        self.session.headers.update({'Referer': constants.BASE_URL, 'user-agent': constants.STORIES_UA})
        req = self.session.get(constants.BASE_URL)

        self.session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})
        self.session.headers.update({'user-agent': constants.CHROME_WIN_UA})
        self.authenticated = True

    def authenticate_with_login(self):
        """Logs in to instagram."""
        self.session.headers.update({'Referer': constants.BASE_URL, 'user-agent': constants.STORIES_UA})
        req = self.session.get(constants.BASE_URL)
        print("req from authenticate: " + str(req))

        self.session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})

        login_data = {'username': self.login_user, 'password': self.login_pass}
        print(str(login_data))
        login = self.session.post(constants.LOGIN_URL, data=login_data, allow_redirects=True)
        self.session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        self.cookies = login.cookies
        login_text = json.loads(login.text)

        print("login_text :" + login.text)
        if login_text.get('authenticated') and login.status_code == 200:
            self.authenticated = True
            self.logged_in = True
            self.session.headers.update({'user-agent': constants.CHROME_WIN_UA})
            self.rhx_gis = ""
        else:
            self.logger.error('Login failed for ' + self.login_user)

            if 'checkpoint_url' in login_text:
                checkpoint_url = login_text.get('checkpoint_url')
                self.logger.error('Please verify your account at ' + constants.BASE_URL[0:-1] + checkpoint_url)
                print('Please verify your account at ' + constants.BASE_URL[0:-1] + checkpoint_url)

                # if self.interactive is True:
                #     self.login_challenge(checkpoint_url)
            elif 'errors' in login_text:
                for count, error in enumerate(login_text['errors'].get('error')):
                    count += 1
                    self.logger.debug('Session error %(count)s: "%(error)s"' % locals())
            else:
                self.logger.error(json.dumps(login_text))

    def get_profile_info(self, username):
        url = constants.USER_URL.format(username)
        resp_text = self.session.get(url).text
        print("response for insta profile info" + resp_text)
        resp = json.loads(resp_text)
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


def main(usernames, insta_login_user, insta_password):

    instagram_scraper = InstagramSimpleScrapper(insta_login_user, insta_password)
    # instagram_scraper.authenticate_as_guest()
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
    args, unknown = CLI.parse_known_args()
    main(args.insta_usernames, args.insta_login_user[0], args.insta_password[0])

