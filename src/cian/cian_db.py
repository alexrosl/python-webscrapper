from random import random

import pandas

from src.db.db_utils import CianProperty, DbUtil


def insert_rows(df, db_util):
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
            db_util.merge(cian_property)
        except:
            print(f"cannot insert property with id {row.at['cian_id']}")


def read_rows():
    query = db_util.read(CianProperty)
    first: CianProperty = query.first()
    print(first)


def update_rows():
    rnd = random()
    query = db_util.read(CianProperty)
    first: CianProperty = query.first()
    to_update = query.filter(CianProperty.id == first.id)
    db_util.update(to_update, {'description': "updated description " + str(rnd)})
    query = db_util.read(CianProperty)
    first: CianProperty = query.first()
    assert str(first.description) == "updated description " + str(rnd)


def delete_row():
    query = db_util.read(CianProperty)
    size_before = query.count()
    first: CianProperty = query.first()
    to_delete = query.filter(CianProperty.id == first.id)
    db_util.delete(to_delete)
    query = db_util.read(CianProperty)
    size_after = query.count()
    assert size_before - 1 == size_after


if __name__ == '__main__':
    df = pandas.read_csv("apartments.csv")
    df = df.where(pandas.notnull(df), None)
    db_util = DbUtil()
    db_util.truncate(CianProperty.__tablename__)
    insert_rows(df, db_util)
