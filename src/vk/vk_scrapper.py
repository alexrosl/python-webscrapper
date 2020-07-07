import argparse
from datetime import datetime
from urllib.parse import urljoin

import pandas
from requests import post

from src.db.db_utils import DbUtil, VkPost

global access_token
BASE_API_URL = "https://api.vk.com/"
BASE_URL = "https://vk.com/"


def get_posts(groups):
    count = 30
    posts = []
    for group in groups:
        r = api('wall.get', count=count, domain=group)
        posts_local = r['response']['items']
        posts.extend([dict(item, author=group) for item in posts_local])
    return posts


def api(method, params=None, **kw):
    params = dict(params or {})
    params.update(kw)
    params.update({
        'v': '5.120',
        'access_token': access_token
    })
    endpoint=urljoin(BASE_API_URL + 'method/', method)
    r=post(endpoint, data=params)
    return r.json()


def main():
    global access_token
    CLI = argparse.ArgumentParser()
    CLI.add_argument(
        "--groups",  # name on the CLI - drop the `--` for positional/required parameters
        nargs="*",  # 0 or more values expected => creates a list
        type=str
    )
    CLI.add_argument(
        "--access_token",  # name on the CLI - drop the `--` for positional/required parameters
        nargs="*",  # 0 or more values expected => creates a list
        type=str
    )
    args = CLI.parse_args()
    access_token = args.access_token
    groups = args.groups
    posts = get_posts(groups)

    pandas.set_option('display.max_colwidth', None)
    df = pandas.DataFrame(posts)
    df = df[(df['text'] != "")]
    df = df.sort_values(by=['date'], ascending=False)
    df[['owner_id', 'id']] = df[['owner_id', 'id']].astype(int).astype(str)
    df["post_url"] = BASE_URL + "wall" + df["owner_id"] + "_" + df["id"]
    df["date"] = df["date"].apply(lambda x: datetime.utcfromtimestamp(x))
    columns = ["author",
               "post_url",
               "text",
               "date"
               ]
    # df.to_csv("insta_posts.csv", header=True, columns=columns)

    db_util = DbUtil()
    # db_util.truncate(VkPost.__tablename__)
    for index, row in df.iterrows():
        vk_post = VkPost(
            post_url=row.at["post_url"],
            author=row.at["author"],
            text=row.at["text"],
            datetime=row.at["date"]
        )
        db_row = db_util.read(VkPost).filter(VkPost.post_url == row.at["post_url"])
        db_util.upsert(db_row, vk_post, VkPost.__tablename__)

    df['post_url'] = df['post_url'].apply(lambda x: '<a href="{0}">Ссылка</a>'.format(x))
    html_template = open("../../templates/report_template.html").read()
    with open("report.html", mode="w") as f:
        f.write(html_template % (3, df.to_html(columns=columns, escape=False, index=False).replace(r"\n", "<br>")))


if __name__ == '__main__':
    main()
