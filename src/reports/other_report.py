import pandas

from src.db.db_utils import DbUtil, OtherInfo


def main():
    pandas.set_option('display.max_colwidth', None)

    db_util = DbUtil()
    df = pandas.read_sql(sql=db_util.read(OtherInfo).statement, con=db_util.db)

    columns = ["source",
               "source_id",
               "author",
               "title",
               "url",
               "datetime",
               "created",
               "modified"
               ]

    df["source"] = df["source"].apply(lambda x: '<a href="{0}">{1}</a>'.format(x, x))
    df['url'] = df['url'].apply(lambda x: '<a href="{0}">Ссылка</a>'.format(x))
    html_template = open("../../templates/report_template.html").read()
    with open("other_report.html", mode="w") as f:
        f.write(html_template % (4, df.to_html(columns=columns, escape=False, index=False).replace(r"\n", "<br>")))


if __name__ == '__main__':
    main()