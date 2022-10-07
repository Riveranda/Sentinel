from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from os import path
import json

Base = declarative_base()

class ServerConfigs(Base):
    __tablename__ = "serverconfigs"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(100), nullable=False)
    channel = Column(Integer, nullable=True, default=None)
    muted = Column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"ServerConfig{self.id}, {self.name}, {self.channel}"

class WatchList(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True)
    system_id = Column(Integer, nullable=False)
    server_id = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"WatchList:{self.id}, {self.server_id}, {self.name}"

class Systems(Base):
    __tablename__ = "systems"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(15), nullable=False)
    constellation_id = Column(Integer, nullable=False)
    def __repr__(self) -> str:
        return f"System:{self.id}, {self.name}, {self.constellation_id}"

class Constellations(Base):
    __tablename__ = "constellations"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(30), nullable=False)
    region_id = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"Constellation:{self.id}, {self.name}, {self.region_id}"

class Regions(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(30), nullable=False)

    def __repr__(self) -> str:
        return f"Regions:{self.id}, {self.name}"


def write_regions_from_json_file(session):
    with open('json/regions.json', 'r') as file:
        obj = json.load(file)
        for key, value in obj.items():
            entry = Regions(id=value[0], name=key)
            session.add(entry)
    session.commit()

def write_systems_from_json_file(session):
    with open('json/systems.json', 'r') as file:
        obj = json.load(file)
        for key, value in obj.items():
            entry = Systems(id=value[0], name=key,
                constellation_id=value[1])
            session.add(entry)
    session.commit()

def write_constellations_from_json_file(session):
    with open('json/constellations.json', 'r') as file:
        obj = json.load(file)
        for key, value in obj.items():
            entry = Constellations(id=value[0], name=key,
                region_id=value[1])
            session.add(entry)
    session.commit()

def create_database(engine, session):
    if not path.exists('database.db'):
        Base.metadata.create_all(engine)

        write_systems_from_json_file(session)
        write_constellations_from_json_file(session)
        write_regions_from_json_file(session)

        print("Database Created!")




