import pandas
import requests
from bs4 import BeautifulSoup
from user_agent import generate_user_agent

from src.db.db_utils import DbUtil, OtherInfo


class MoyaPlaneta:
    def __init__(self):
        self.base_url = "https://moaplaneta.com/"

    def get_events(self):
        url = self.base_url + "meropriyatiya/"
        headers = {"User-Agent": generate_user_agent(device_type="desktop", os=("mac", "linux"))}
        response = requests.get(url, headers=headers)
        html_soup = BeautifulSoup(response.text, 'html.parser')
        containers = html_soup.find_all("div", attrs={"class": "class-item"})
        events = []
        count = len(containers)
        for container in containers:
            d = {}
            content = container.find("div", attrs={"class": "content"})
            d["title"] = content.find("a").text
            d["url"] = content.find("a")['href']
            try:
                d["description"] = content.find_all("p")[1].text
            except :
                d["description"] = None
            d["date"] = container.find("span", attrs={"class": "moreinfo"}).text
            d["address"] = container.find("div", attrs={"class": "address"}).text
            count -= 1
            events.append(d)
        return events

    def write_info(self, events):
        df = pandas.DataFrame(events)
        df["source"] = self.base_url

        columns = ["source",
                   "url",
                   "title",
                   "description",
                   "date"
                   ]
        # df.to_csv("insta_posts.csv", header=True, columns=columns)

        db_util = DbUtil()
        tablename = OtherInfo.__tablename__
        # db_util.truncate(OtherInfo.__tablename__)
        for index, row in df.iterrows():
            moya_planet_post = OtherInfo(
                source=row.at["source"],
                url=row.at["url"],
                description=row.at["description"],
                date=row.at["date"],
                address=row.at["address"]
            )
            db_row = db_util.read(OtherInfo).filter(OtherInfo.url == row.at["url"] and OtherInfo.source == row.at["source"])
            db_util.upsert(db_row, moya_planet_post, tablename)

        df["source"] = df["source"].apply(lambda x: '<a href="{0}">{1}</a>'.format(x, x))
        df['url'] = df['url'].apply(lambda x: '<a href="{0}">Ссылка</a>'.format(x))
        html_template = open("../../templates/report_template.html").read()
        with open("report.html", mode="w") as f:
            f.write(html_template % (5, df.to_html(columns=columns, escape=False, index=False).replace(r"\n", "<br>")))


if __name__ == '__main__':
    planeta = MoyaPlaneta()
    events = planeta.get_events()
    planeta.write_info(events)
