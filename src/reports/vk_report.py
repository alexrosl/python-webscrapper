import pandas

from src.db.db_utils import DbUtil, VkPost


def main():
    pandas.set_option('display.max_colwidth', None)

    db_util = DbUtil()
    df = pandas.read_sql(sql=db_util.read(VkPost).statement, con=db_util.db)

    columns = ["author",
               "post_id",
               "post_url",
               "text",
               "datetime",
               "created",
               "modified"
               ]

    df['post_url'] = df['post_url'].apply(lambda x: '<a href="{0}">Ссылка</a>'.format(x))
    html_template = open("../../templates/report_template.html").read()
    with open("vk_report.html", mode="w") as f:
        f.write(html_template % (4, df.to_html(columns=columns, escape=False, index=False).replace(r"\n", "<br>")))


if __name__ == '__main__':
    main()