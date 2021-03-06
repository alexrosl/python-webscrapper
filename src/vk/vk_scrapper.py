import argparse
from datetime import datetime
from urllib.parse import urljoin

import pandas
from requests import post

from src.db.db_utils import DbUtil, VkPost

global access_token
BASE_API_URL = "https://api.vk.com/"
BASE_URL = "https://vk.com/"


def get_posts(groups, access_token):
    count = 30
    posts = []
    for group in groups:
        r = api('wall.get', access_token, count=count, domain=group)
        posts_local = r['response']['items']
        posts.extend([dict(item, author=group) for item in posts_local])
    return posts


def api(method, access_token, params=None, **kw):
    params = dict(params or {})
    params.update(kw)
    params.update({
        'v': '5.120',
        'access_token': access_token
    })
    endpoint=urljoin(BASE_API_URL + 'method/', method)
    r=post(endpoint, data=params)
    return r.json()


def main(groups, access_token):

    posts = get_posts(groups, access_token)
    print("Received vk posts " + str(len(posts)))

    pandas.set_option('display.max_colwidth', None)
    df = pandas.DataFrame(posts)
    df = df[(df['text'] != "")]
    df = df.sort_values(by=['date'], ascending=False)
    df[['owner_id', 'id']] = df[['owner_id', 'id']].astype(int).astype(str)
    df["post_id"] = df["owner_id"] + "_" + df["id"]
    df["post_url"] = BASE_URL + "wall" + df["owner_id"] + "_" + df["id"]
    df["date"] = df["date"].apply(lambda x: datetime.utcfromtimestamp(x))

    # df.to_csv("insta_posts.csv", header=True, columns=columns)

    db_util = DbUtil()
    # db_util.truncate(VkPost.__tablename__)
    for index, row in df.iterrows():
        vk_post = VkPost(
            post_id=row.at["post_id"],
            post_url=row.at["post_url"],
            author=row.at["author"],
            text=row.at["text"],
            datetime=row.at["date"]
        )
        db_row = db_util.read(VkPost).filter(VkPost.post_url == row.at["post_url"])
        db_util.upsert(db_row, vk_post, VkPost.__tablename__)


if __name__ == '__main__':
    CLI = argparse.ArgumentParser()
    CLI.add_argument(
        "--vk_groups",  # name on the CLI - drop the `--` for positional/required parameters
        nargs="*",  # 0 or more values expected => creates a list
        type=str
    )
    CLI.add_argument(
        "--vk_access_token",  # name on the CLI - drop the `--` for positional/required parameters
        nargs="*",  # 0 or more values expected => creates a list
        type=str
    )
    args, unknown = CLI.parse_known_args()
    access_token = args.vk_access_token
    groups = args.vk_groups
    main(groups, access_token)
