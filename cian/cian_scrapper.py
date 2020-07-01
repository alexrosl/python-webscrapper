import re

import pandas
import requests
from bs4 import BeautifulSoup


def scrap_page(apart_containers_):
    for apart in apart_containers_:
        d = {}
        try:
            d['link'] = apart.find("a", attrs={"class": regexps["link"]})["href"]
            d['cian_id'] = int(d['link'].split("/")[-2])
        except:
            d['link'] = None

        try:
            d['title'] = apart.find("div", attrs={"class": regexps["title"]}).text
        except:
            try:
                d['title'] = apart.find("div", attrs={"class": regexps["title2"]}).text
            except:
                d['title'] = None

        try:
            attributes = apart.find("div", attrs={"class": regexps["subtitle"]}).text
            d["attributes"] = attributes
            d["area"] = attributes.split(",")[1].split(" ")[1]
        except:
            if d['title'] is not None:
                d['attributes'] = d['title']
                d["area"] = d['attributes'].split(",")[1].split(" ")[1]
        try:
            d['metro'] = apart.find("div", attrs={"class": regexps["metro"]}).text
        except:
            d['metro'] = None

        try:
            d['remoteness'] = apart.find("div", attrs={"class": regexps["remoteness"]}).text
            if "пешком" in d['remoteness']:
                d['walk'] = True
        except:
            d['remoteness'] = None

        try:
            d['address'] = apart.find("div", attrs={"data-name": "AddressItem"}).text
        except:
            d['address'] = None

        try:
            price_container = apart.find("div", attrs={"data-name": regexps["price-container"]})
            try:
                price_full = price_container.find("div", attrs={"class": regexps["price-full"]}).text.replace(" ", "")
                d["price_full"] = int(re.search(regexps["price_digit"], price_full).group(1))
                d["currency"] = re.search(regexps["price_currency"], price_full).group(1)
            except:
                d['price_full'] = None
                d["currency"] = None
            try:
                price_per_meter = price_container.find("div", attrs={"class": regexps["price-per-meter"]}).text.replace(" ", "")
                d["price_per_meter"] = int(re.search(regexps["price_digit"], price_per_meter).group(1))
            except:
                d['price_per_meter'] = None
        except:
            pass

        try:
            d['description'] = apart.find("div", attrs={"data-name": regexps["description"]}).text
        except:
            d['description'] = None

        list_.append(d)


regexps = {
    "offerCard": re.compile("--offer-container--"),
    "link": re.compile(".*--header--.*"),
    "title": re.compile(".*--title--.*"),
    "title2": re.compile(".*--single_title--.*"),
    "subtitle": re.compile(".*--subtitle--.*"),
    "metro": re.compile(".*--underground-name--.*"),
    "remoteness": re.compile(".*--remoteness--.*"),
    "price-container": re.compile(".*Price.*"),
    "price-full": re.compile(".*--header--.*"),
    "price-per-meter": re.compile(".*--term--.*"),
    "description": re.compile("Description"),

    "price_digit": re.compile("^(\d*)"),
    "price_currency": re.compile("(\D*)$")
}

headers = ({'User-Agent':
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'})


url = "https://www.cian.ru/cat.php"

params = {
    "currency": "2",
    "deal_type": "sale",
    "engine_version": "2",
    "is_first_floor": "0",
    "maxprice": "7000000",
    "minfloorn": "6",
    "mintarea": "40",
    "object_type%5B0%5D": "1",
    "offer_type": "flat",
    "region": "1",
    "room2": "1"
}
list_ = []


response = requests.get(url, params=params, headers=headers)
html_soup = BeautifulSoup(response.text, 'html.parser')
total_ads_summary = html_soup.find("div", attrs={"data-name": "SummaryHeader"}).text
total_ads_count = int(re.search(r"Найдено (\d*) объявлен", total_ads_summary).group(1))
apart_containers = html_soup.find_all("div", attrs={"class": regexps["offerCard"]})
scrap_page(apart_containers)

for i in range(2, int(total_ads_count / len(apart_containers)) + 1):
    params["p"] = str(i)
    response = requests.get(url, params=params, headers=headers)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    apart_containers = html_soup.find_all("div", attrs={"class": regexps["offerCard"]})
    scrap_page(apart_containers)


df = pandas.DataFrame(list_)
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
df.to_csv("apartments.csv", header=True, columns=columns)
