import pandas

from db.db_utils import CianProperty, DbUtil

df = pandas.read_csv("apartments.csv")
df = df.where(pandas.notnull(df), None)
db_util = DbUtil()

for index, row in df.iterrows():
    try:
        area = int(row.at["area"])
    except:
        area = None
    try:
        walk = bool(row.at["walk"])
    except:
        walk = None
    try:
        price_full = int(row.at["price_full"])
    except:
        price_full = None
    try:
        price_per_meter = int(row.at["price_per_meter"])
    except:
        price_per_meter = None

    cian_property = CianProperty(
        cian_id=int(row.at["cian_id"]),
        link=row.at["link"],
        title=row.at["title"],
        attributes=row.at["attributes"],
        area=area,
        metro=row.at["metro"],
        remoteness=row.at["remoteness"],
        walk=walk,
        address=row.at["address"],
        price_full=price_full,
        price_per_meter=price_per_meter,
        currency=row.at["currency"],
        description=row.at["description"]
    )

    try:
        db_util.create(cian_property)
    except:
        print(f"cannot insert property with id {row.at['cian_id']}")

