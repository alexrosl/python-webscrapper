import pandas
from flask import render_template, Blueprint
from flask_login import login_required

from src.db.db_utils import DbUtil

main = Blueprint('main', __name__)


@main.route("/")
@login_required
def index():
    pandas.set_option('display.max_colwidth', None)
    query = open("src/all/all_resources.sql", "r").read()

    db_util = DbUtil()
    df = pandas.read_sql(sql=query, con=db_util.db)
    df["author"] = df["source"] + "\n" + df["author"]
    columns = [
               "author",
               "link",
               "text",
               "datetime",
               "created"
               ]
    df['link'] = df['link'].apply(lambda x: '<a href="{0}">Ссылка</a>'.format(x))

    html_text = df.to_html(columns=columns, escape=False, index=False).replace(r"\n", "<br>")
    return render_template("index_template.html", text=html_text, order_column="4")
