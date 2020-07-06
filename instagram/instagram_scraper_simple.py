import argparse
import json
from datetime import datetime

import pandas
import requests

import instagram.constants as constants
from db.db_utils import DbUtil, InstagramPost


class InstagramSimpleScrapper(object):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {'user-agent': constants.CHROME_LINUX_UA}

    def authenticate_as_guest(self):
        """Authenticate as a guest/non-signed in user"""
        self.session.headers.update({'Referer': constants.BASE_URL, 'user-agent': constants.STORIES_UA})
        req = self.session.get(constants.BASE_URL)

        self.session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})
        self.session.headers.update({'user-agent': constants.CHROME_LINUX_UA})
        self.authenticated = True

    def get_profile_info(self, username):
        url = constants.USER_URL.format(username)
        resp_text = self.session.get(url).text
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


if __name__ == '__main__':
    CLI = argparse.ArgumentParser()
    CLI.add_argument(
        "--usernames",  # name on the CLI - drop the `--` for positional/required parameters
        nargs="*",  # 0 or more values expected => creates a list
        type=str
    )
    args = CLI.parse_args()

    usernames = args.usernames
    instagram_scraper = InstagramSimpleScrapper()
    instagram_scraper.authenticate_as_guest()
    posts = instagram_scraper.get_posts(usernames)

    pandas.set_option('display.max_colwidth', None)
    df = pandas.DataFrame(posts)
    df = df.sort_values(by=['datetime'], ascending=False)
    columns = ["insta_id",
               "link",
               "author",
               "text",
               "datetime"]
    # df.to_csv("insta_posts.csv", header=True, columns=columns)

    db_util = DbUtil()
    for index, row in df.iterrows():
        insta_post = InstagramPost(
            insta_id=row.at["insta_id"],
            link=row.at["link"],
            author=row.at["author"],
            text=row.at["text"],
            datetime=row.at["datetime"])
        try:
            db_util.create(insta_post)
        except:
            print(f"cannot insert post with id {row.at['insta_id']}")

    df['link'] = df['link'].apply(lambda x: '<a href="{0}">Ссылка</a>'.format(x))
    html_template = open("../templates/report_template.html").read()
    with open("report.html", mode="w") as f:
        f.write(html_template % (4, df.to_html(columns=columns, escape=False, index=False).replace(r"\n", "<br>")))

