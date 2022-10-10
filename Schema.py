from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from os import path
from json import load

Base = declarative_base()


class ServerConfigs(Base):
    __tablename__ = "serverconfigs"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(100), nullable=False)
    channel = Column(Integer, nullable=True, default=None)
    muted = Column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"ServerConfig{self.id}, {self.name}, {self.channel}"


class WatchLists(Base):
    __tablename__ = "watchlists"

    server_id = Column(Integer, primary_key=True, autoincrement=False)
    systems = Column(String(5000), nullable=False, default="[]")
    constellations = Column(String(1000), nullable=False, default="[]")
    regions = Column(String(500), nullable=False, default="[]")
    corporations = Column(String(2000), nullable=False, default="[]")
    alliances = Column(String(500), nullable=False, default="[]")
    players = Column(String(1000), nullable=False, default="[]")

    def __repr__(self) -> str:
        return f"WatchList:{self.id}, {self.server_id}, {self.name}"


class Systems(Base):
    __tablename__ = "systems"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(30), nullable=False, index=True)
    constellation_id = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"System:{self.id}, {self.name}, {self.constellation_id}"


class Constellations(Base):
    __tablename__ = "constellations"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(30), nullable=False, index=True)
    region_id = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"Constellation:{self.id}, {self.name}, {self.region_id}"


class Regions(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(30), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"Region:{self.id}, {self.name}"


class Corporations(Base):
    __tablename__ = "corporations"

    id = Column(Integer, primary_key=True, autoincrement=False)
    alliance_id = Column(Integer, nullable=True, default=None)
    name = Column(String(51), nullable=False, index=True)
    ticker = Column(String(6), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"Corporation:{self.id}, {self.name}:{self.ticker}, Alliance_id:{self.alliance_id}"


class Alliances(Base):
    __tablename__ = "alliances"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(51), nullable=False, index=True)
    ticker = Column(String(6), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"Alliance:{self.id}, {self.name}:{self.ticker}"


def write_regions_from_json_file(session):
    with open('json/regions.json', 'r') as file:
        obj = load(file)
        for key, value in obj.items():
            entry = Regions(id=key, name=value[0])
            session.add(entry)
    session.commit()


def write_systems_from_json_file(session):
    with open('json/systems.json', 'r') as file:
        obj = load(file)
        for key, value in obj.items():
            entry = Systems(id=key, name=value[0],
                            constellation_id=value[1])
            session.add(entry)
    session.commit()


def write_constellations_from_json_file(session):
    with open('json/constellations.json', 'r') as file:
        obj = load(file)
        for key, value in obj.items():
            entry = Constellations(id=key, name=value[0],
                                   region_id=value[1])
            session.add(entry)
    session.commit()


def write_corporations_from_json_file(session):
    with open('json/corporations.json', 'r') as file:
        obj = load(file)
        for key, value in obj.items():
            entry = Corporations(id=key, name=value[0],
                                 alliance_id=value[1], ticker=value[2])
            session.add(entry)
    session.commit()


def write_alliances_from_json_file(session):
    with open('json/alliances.json', 'r') as file:
        obj = load(file)
        for key, value in obj.items():
            entry = Alliances(id=key, name=value[0], ticker=value[1])
            session.add(entry)
    session.commit()


def write_system_configurations_from_json_file(session):
    with open('json/server_configs.json', 'r') as file:
        obj = load(file)
        for key, value in obj.items():
            entry = ServerConfigs(
                id=key, name=value[0], channel=value[1], muted=value[2])
            session.add(entry)
    session.commit()


def create_database():
    if not path.exists('database.db'):
        from commands import Session, engine
        session = Session()
        Base.metadata.create_all(engine)

        write_systems_from_json_file(session)
        write_constellations_from_json_file(session)
        write_regions_from_json_file(session)
        write_corporations_from_json_file(session)
        write_alliances_from_json_file(session)
        write_system_configurations_from_json_file(session)

        Session.remove()
        print("Database Created!")
