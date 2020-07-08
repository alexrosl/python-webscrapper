import pandas

from src.db.db_utils import DbUtil


def generate_report():
    pandas.set_option('display.max_colwidth', None)
    query = open("src/all/all_resources.sql", "r").read()

    db_util = DbUtil()
    df = pandas.read_sql(sql=query, con=db_util.db)

    columns = ["source",
               "id",
               "author",
               "link",
               "text",
               "datetime",
               "created"
               ]

    df['link'] = df['link'].apply(lambda x: '<a href="{0}">Ссылка</a>'.format(x))
    html_template = open("templates/report_template.html").read()
    with open("full_report.html", mode="w") as f:
        f.write(html_template % (5, df.to_html(columns=columns, escape=False, index=False).replace(r"\n", "<br>")))


if __name__ == '__main__':
    generate_report()