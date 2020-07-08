import pandas

from src.db.db_utils import DbUtil, FacebookPost


def main():
    pandas.set_option('display.max_colwidth', None)

    db_util = DbUtil()
    df = pandas.read_sql(sql=db_util.read(FacebookPost).statement, con=db_util.db)

    columns = ["post_id",
               "link",
               "author",
               "text",
               "datetime",
               "created",
               "modified"
               ]

    df['link'] = df['link'].apply(lambda x: '<a href="{0}">Ссылка</a>'.format(x))
    html_template = open("../../templates/report_template.html").read()
    with open("facebook_report.html", mode="w") as f:
        f.write(html_template % (4, df.to_html(columns=columns, escape=False, index=False).replace(r"\n", "<br>")))


if __name__ == '__main__':
    main()