from datetime import datetime

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
            datetime_str = container.find("span", attrs={"class": "moreinfo"}).text
            try:
                d["datetime"] = datetime.strptime(datetime_str, '%d.%m.%Y')
            except:
                d["datetime"] = None
                d["description"] = datetime_str.upper() + "\n" + d["description"]

            address = container.find("div", attrs={"class": "address"}).text
            d["description"] = d["description"] + "\n" + address
            count -= 1
            events.append(d)
        return events

    def write_info(self, events):
        df = pandas.DataFrame(events)
        df["source"] = self.base_url
        df["datetime"] = df["datetime"].astype(object).where(df["datetime"].notnull(), None)

        # df.to_csv("insta_posts.csv", header=True, columns=columns)

        db_util = DbUtil()
        tablename = OtherInfo.__tablename__
        # db_util.truncate(OtherInfo.__tablename__)
        for index, row in df.iterrows():

            moya_planet_post = OtherInfo(
                source=row.at["source"],
                url=row.at["url"],
                title=row.at["title"],
                text=row.at["description"],
                datetime=row.at["datetime"]
            )
            db_row = db_util.read(OtherInfo).filter(OtherInfo.url == row.at["url"] and OtherInfo.source == row.at["source"])
            db_util.upsert(db_row, moya_planet_post, tablename)


if __name__ == '__main__':
    planeta = MoyaPlaneta()
    events = planeta.get_events()
    planeta.write_info(events)
