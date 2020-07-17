import copy
import re
from datetime import datetime

import pandas
import requests
from bs4 import BeautifulSoup
from user_agent import generate_user_agent

from src.db.db_utils import DbUtil, OtherInfo


class BaseOther:
    def __init__(self, base_url):
        self.base_url = base_url

    def write_info(self, events):
        df = pandas.DataFrame(events)
        df["source"] = self.base_url
        df["datetime"] = df["datetime"].astype(object).where(df["datetime"].notnull(), None)


        db_util = DbUtil()
        tablename = OtherInfo.__tablename__
        # db_util.truncate(OtherInfo.__tablename__)
        for index, row in df.iterrows():

            post = OtherInfo(
                source=row.at["source"],
                url=row.at["url"],
                text=row.at["description"],
                datetime=row.at["datetime"]
            )
            db_row = db_util.read(OtherInfo).filter(OtherInfo.url == row.at["url"], OtherInfo.source == row.at["source"], OtherInfo.datetime == row.at["datetime"])
            db_util.upsert(db_row, post, tablename)


class MoyaPlaneta(BaseOther):
    def __init__(self, base_url):
        super().__init__(base_url)

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
            d["description"] = content.find("a").text
            d["url"] = content.find("a")['href']
            try:
                d["description"] = d["description"] + "\n" + content.find_all("p")[1].text
            except:
                pass
            datetime_str = container.find("span", attrs={"class": "moreinfo"}).text
            try:
                d["datetime"] = datetime.strptime(datetime_str, '%d.%m.%Y')
            except:
                d["datetime"] = None
                d["description"] = datetime_str.upper() + "\n" + d["description"]

            address = container.find("div", attrs={"class": "address"}).text
            if address is not None:
                d["description"] = d["description"] + "\n" + address
            count -= 1
            events.append(d)
        return events

    def main(self):
        events = self.get_events()
        print("Received planeta events " + str(len(events)))
        self.write_info(events)


class AbaKursCom(BaseOther):
    def __init__(self, base_url):
        super().__init__(base_url)
        self.face_to_face = self.base_url + "ochnye-kursy-po-aba"
        self.distant_specialist = self.base_url + "distantsionnye-kursy-po-aba"
        self.distant_parent = self.base_url + "kursy-aba-dlya-roditelej"
        self.distant_training = self.base_url + "distantsionnye-treningi/"
        self.headers = {"User-Agent": generate_user_agent(device_type="desktop", os=("mac", "linux"))}

    def get_events(self):
        events = []
        events.extend(self.scrap_page(self.face_to_face, "Очные курсы для специалистов"),)
        events.extend(self.scrap_page(self.distant_specialist, "Дистанционные курсы для специалистов"))
        events.extend(self.scrap_page(self.distant_parent, "Дистанционные курсы для родителей"))
        return events

    def scrap_page(self, url, descr):
        response = requests.get(url, headers=self.headers)
        html_soup = BeautifulSoup(response.text, 'html.parser')
        container = html_soup.find("div", class_="in-course last").find("table")
        rows = container.find_all("tr", attrs={"class": None}) # skip header
        events = []
        for row in rows:
            d = {}
            d["description"] = descr + "\n"
            d["description"] = d["description"] + "Курс №" + row.find_all("td")[0].text
            d["description"] = d["description"] + " " + row.find_all("td")[1].text + ". "
            d["description"] = d["description"] + "\n" + "Стоимость: " + row.find_all("td")[2].text + "\n"
            datetime_link = row.find_all("td")[3]
            datetime_strs = datetime_link.find_all("div", attrs={"class": "line"})
            for datetime_str in datetime_strs:
                d_local = copy.deepcopy(d)
                datetime_start_str = re.search(r"с (\S*) по (\S*)", datetime_str.find("p").text).group(1)
                try:
                    d_local["datetime"] = datetime.strptime(datetime_start_str, '%d.%m.%Y')
                except:
                    d_local["description"] = datetime_str.find("p").upper() + "\n" + d_local["description"]

                try:
                    d_local["url"] = url + "/" + datetime_str.find("a")["href"]
                except:
                    d_local["url"] = None
                events.append(d_local)
        return events

    def main(self):
        events = self.get_events()
        print("Received aba-kurs.com events " + str(len(events)))
        self.write_info(events)


def main():
    moya_planeta = MoyaPlaneta("https://moaplaneta.com/")
    moya_planeta.main()

    aba_kurs = AbaKursCom("https://aba-kurs.com/")
    aba_kurs.main()


if __name__ == '__main__':
    main()
