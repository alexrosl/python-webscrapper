from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Query

db_string = "postgres://postgres:postgres@localhost:5432/webscrapper"
base = declarative_base()


class InstagramPost(base):
    __tablename__ = 'instagram_posts'
    id = Column(Integer, primary_key=True)
    insta_id = Column(String, index=True)
    link = Column(String)
    author = Column(String)
    text = Column(String)
    datetime = Column(DateTime)


class CianProperty(base):
    __tablename__ = 'cian_properties'

    id = Column(Integer, primary_key=True)
    cian_id = Column(Integer, index=True, nullable=False)
    link = Column(String, nullable=False)
    title = Column(String)
    attributes = Column(String)
    area = Column(Integer)
    metro = Column(String)
    remoteness = Column(String)
    walk = Column(Boolean, default=False)
    address = Column(String)
    price_full = Column(Integer)
    price_per_meter = Column(Integer)
    currency = Column(String)
    description = Column(String)

    def __str__(self) -> str:
        return str(self.id) + " " + str(self.cian_id) + " " + str(self.title) + " " + str(self.description)


class DbUtil:
    def __init__(self):
        db = create_engine(db_string)

        Session = sessionmaker(db)
        self.session = Session()

        base.metadata.create_all(db)

    def create(self, obj):
        self.session.add(obj)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise

    def read(self, entity) -> Query:
        objects = self.session.query(entity)
        return objects

    def update(self, entity, dict_values):
        entity.update(dict_values)
        self.session.commit()

    def delete(self, obj):
        obj.delete()
        self.session.commit()

    def truncate(self, table):
        self.session.execute(f"TRUNCATE TABLE {table}")
        self.session.commit()





