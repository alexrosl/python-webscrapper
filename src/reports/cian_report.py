import pandas

from src.db.db_utils import DbUtil, CianProperty


def main():
    pandas.set_option('display.max_colwidth', None)

    db_util = DbUtil()
    df = pandas.read_sql(sql=db_util.read(CianProperty).statement, con=db_util.db)

    columns = ["cian_id",
               "link",
               "title",
               "attributes",
               "area",
               "metro",
               "remoteness",
               "walk",
               "address",
               "price_full",
               "price_per_meter",
               "currency",
               "description"]

    df['link'] = df['link'].apply(lambda x: '<a href="{0}">Ссылка</a>'.format(x))
    html_template = open("../../templates/report_template.html").read()
    with open("cian_report.html", mode="w") as f:
        f.write(html_template % (8, df.to_html(columns=columns, escape=False, index=False)))


if __name__ == '__main__':
    main()