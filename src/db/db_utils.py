import datetime

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Sequence
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Query

db_string = "postgres://postgres:postgres@localhost:5432/webscrapper"
base = declarative_base()


class Base(object):
    def __tablename__(self):
        return self.__name__.lower()
    created = Column(DateTime(timezone=True))
    modified = Column(DateTime(timezone=True))


Base = declarative_base(cls=Base)


class OtherInfo(Base):
    __tablename__ = "other_info"
    id_seq = Sequence('other_info_sequence', metadata=Base.metadata)
    id = Column(Integer, id_seq, primary_key=True)
    source = Column(String)
    source_id = Column(String)
    author = Column(String)
    title = Column(String)
    url = Column(String)
    text = Column(String)
    datetime = Column(DateTime)


class VkPost(Base):
    __tablename__ = "vk_posts"
    id_seq = Sequence('vk_sequence', metadata=Base.metadata)
    id = Column(Integer, id_seq, primary_key=True)
    post_id = Column(String, index=True)
    post_url = Column(String)
    author = Column(String)
    text = Column(String)
    datetime = Column(DateTime)


class FacebookPost(Base):
    __tablename__ = 'facebook_posts'
    id_seq = Sequence('facebook_sequence', metadata=Base.metadata)
    id = Column(Integer, id_seq, primary_key=True)
    post_id = Column(String, index=True, primary_key=True)
    link = Column(String)
    author = Column(String)
    text = Column(String)
    datetime = Column(DateTime)


class InstagramPost(Base):
    __tablename__ = 'instagram_posts'
    id_seq = Sequence('insta_sequence', metadata=Base.metadata)
    id = Column(Integer, id_seq, primary_key=True)
    insta_id = Column(String, index=True, primary_key=True)
    link = Column(String)
    author = Column(String)
    text = Column(String)
    datetime = Column(DateTime)


class CianProperty(base):
    __tablename__ = 'cian_properties'

    id = Column(Integer)
    cian_id = Column(Integer, index=True, nullable=False, primary_key=True)
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
        self.db = create_engine(db_string)

        Session = sessionmaker(self.db)
        self.session = Session()

        base.metadata.create_all(self.db)

    def merge(self, obj):
        self.session.merge(obj)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise

    def upsert(self, db_row, obj, tablename):
        if db_row.scalar() is not None:
            obj.modified = datetime.datetime.utcnow()
            obj.id = db_row.first().id
            try:
                self.merge(obj)
            except:
                print(f"cannot update record in table {tablename} with id {obj.id}")
        else:
            obj.created = datetime.datetime.utcnow()
            obj.modified = obj.created
            try:
                self.merge(obj)
            except:
                print(f"cannot insert record into table {tablename}")

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





