from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db_string = "postgres://postgres:postgres@localhost:5432/webscrapper"
base = declarative_base()


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





