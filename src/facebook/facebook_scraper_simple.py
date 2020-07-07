import argparse

import pandas
from facebook_scraper import get_posts

from src.db.db_utils import DbUtil, FacebookPost


def scrape_accounts(accounts):
    posts = []
    for account in accounts:
        for post in get_posts(account, pages=5):
            post['account'] = account
            posts.append(post)
    return posts


def main():
    CLI = argparse.ArgumentParser()
    CLI.add_argument(
        "--accounts",  # name on the CLI - drop the `--` for positional/required parameters
        nargs="*",  # 0 or more values expected => creates a list
        type=str
    )
    args = CLI.parse_args()

    accounts = args.accounts
    posts = scrape_accounts(accounts)

    pandas.set_option('display.max_colwidth', None)
    df = pandas.DataFrame(posts)
    df = df.sort_values(by=['time'], ascending=False)
    df = df[(df['text'] != "")]
    df = df[df['post_url'].notnull()]
    columns = ["post_id",
               "account",
               "post_url",
               "text",
               "time"
               ]

    db_util = DbUtil()
    # db_util.truncate(FacebookPost.__tablename__)
    for index, row in df.iterrows():
        facebook_post = FacebookPost(
            post_id=row.at["post_id"],
            author=row.at["account"],
            link=row.at["post_url"],
            text=row.at["text"],
            datetime=row.at["time"]
        )
        db_row = db_util.read(FacebookPost).filter(FacebookPost.post_id == row.at["post_id"])
        db_util.upsert(db_row, facebook_post, FacebookPost.__tablename__)

    df['post_url'] = df['post_url'].apply(lambda x: '<a href="{0}">Ссылка</a>'.format(x))
    html_template = open("../../templates/report_template.html").read()
    with open("report.html", mode="w") as f:
        f.write(html_template % (4, df.to_html(columns=columns, escape=False, index=False).replace(r"\n", "<br>")))


if __name__ == '__main__':
    main()
