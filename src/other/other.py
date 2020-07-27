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
            db_row = db_util.read(OtherInfo).filter(OtherInfo.url == row.at["url"],
                                                    OtherInfo.source == row.at["source"],
                                                    OtherInfo.datetime == row.at["datetime"])
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
        events.extend(self.scrap_page(self.face_to_face, "Очные курсы для специалистов"), )
        events.extend(self.scrap_page(self.distant_specialist, "Дистанционные курсы для специалистов"))
        events.extend(self.scrap_page(self.distant_parent, "Дистанционные курсы для родителей"))
        return events

    def scrap_page(self, url, descr):
        response = requests.get(url, headers=self.headers)
        html_soup = BeautifulSoup(response.text, 'html.parser')
        container = html_soup.find("div", class_="in-course last").find("table")
        rows = container.find_all("tr", attrs={"class": None})  # skip header
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


class LogoMaster(BaseOther):
    def __init__(self, base_url):
        super().__init__(base_url)
        self.event_calendar = self.base_url + "xview/xview1.php?m=24&tid=0&t=1&cid=undefined"
        self.headers = {
            "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}

    def get_events(self):
        events = []
        events.extend(self.scrap_page(self.event_calendar))
        return events

    def scrap_page(self, url):
        response = requests.get(url, headers=self.headers)
        html_soupt = BeautifulSoup(response.text, "html.parser")
        table_body = html_soupt.find("table", attrs={"class": re.compile("logoped_table1")})
        rows = table_body.find_all("tr")
        events = []
        for row in rows[1:]:  # could be too many
            d = {}
            datetime_str = row.find_all("td")[0].text.split(" ")[0]
            d["datetime"] = datetime.strptime(datetime_str, '%d.%m.%Y')
            d["description"] = row.find_all("td")[1].find_all("a")[0].text
            d["url"] = row.find_all("td")[1].find_all("a")[0]["href"]
            d["description"] = d["description"] + "\nДополнительная информация:\nПреподаватель:" + row.find_all("td")[
                2].text + "\n"
            d["description"] = d["description"] + "Цена:" + row.find_all("td")[3].text + "\n"
            d["description"] = d["description"] + "Время проведения:" + row.find_all("td")[0].text + "\n" + \
                               row.find_all("td")[4].text
            events.append(d)
        return events

    def chunks(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    def main(self):
        events = self.get_events()
        print("Received logopedmaster.ru events " + str(len(events)))
        self.write_info(events)


class IIOSP(BaseOther):
    def __init__(self, base_url):
        super().__init__(base_url)
        self.headers = {"User-Agent": generate_user_agent(device_type="desktop", os=("mac", "linux"))}
        
    def get_events(self):
        events = []
        events.extend(self.scrap_page())
        return events
        
    def scrap_page(self):
        response = requests.get(self.base_url, headers=self.headers)
        html_soup = BeautifulSoup(response.text, "html.parser")
        articles = html_soup.find_all("article", attrs={"class": re.compile("post")})
        events = []
        for article in articles:
            d = {}
            d["description"] = article.find("header").find("a").text
            d["url"] = article.find("header").find("a")["href"]
            datetime_str = article.find("span", class_="posted-on").find("time").text
            d["datetime"] = datetime.strptime(datetime_str, '%d.%m.%Y')
            d["description"] = d["description"] + "\n" + article.find("div", attrs={"class": re.compile("entry-content")}).find("p").text
            events.append(d)
        return events

    def main(self):
        events = self.get_events()
        print(f"Received internation institue speech pathology events {str(len(events))}")
        self.write_info(events)

        

def main():
    moya_planeta = MoyaPlaneta("https://moaplaneta.com/")
    moya_planeta.main()

    aba_kurs = AbaKursCom("https://aba-kurs.com/")
    aba_kurs.main()

    logo_master = LogoMaster("https://www.logopedmaster.ru/")
    logo_master.main()

    iiosp = IIOSP("http://iiosp.com/")
    iiosp.main()


if __name__ == '__main__':
    main()
