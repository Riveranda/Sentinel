
from discord import Interaction
from functools import lru_cache
from ujson import loads, dumps
from sqlalchemy import or_
from requests import get
from Schema import *


@lru_cache(maxsize=50)
def is_server_channel_set(id: int, session):
    result = session.query(ServerConfigs).get(id)
    if result != None:
        return not result.channel == None
    return False


def create_new_guild(channel_id: int, guild, session, color=None):
    result = session.query(ServerConfigs).get(guild.id)
    if result == None:
        config = ServerConfigs(id=guild.id, name=guild.name,
                               channel=channel_id, muted=False, color=None)
        session.add(config)
    result = session.query(WatchLists).get(guild.id)
    if result == None:
        wlist = WatchLists(server_id=guild.id)
        session.add(wlist)
    session.commit()


def set_filter_to_all(guild_id: int, session):
    filter = does_server_have_filter(guild_id, session)
    if filter == None:
        filter = WatchLists(server_id=guild_id)
        session.add(filter)
    else:
        filter.systems = "[]"
        filter.constellations = "[]"
        filter.regions = "[]"
        filter.corporations = "[]"
        filter.alliances = "[]"
        filter.players = "[]"
    session.commit()


def set_neutral_color_for_guild(interaction: Interaction, color, session):
    result = session.query(ServerConfigs).get(interaction.guild_id)
    if result == None:
        create_new_guild(interaction.channel_id,
                         interaction.guild, session, color=color)
    else:
        result.neutral_color = color
        session.commit()


def get_channel_id_from_guild_id(session, id: int):
    return session.query(ServerConfigs).get(id).channel


def update_server_muted(session, interaction: Interaction, status: bool):
    results = session.query(ServerConfigs).get(interaction.guild.id)
    if results == None:
        update_server_channel(session, interaction, status=status)
    else:
        results.muted = status
        session.commit()


def is_server_muted(session, id: int):
    result = session.query(ServerConfigs).get(id)
    if result != None:
        return result.muted
    return True


def does_server_have_filter(guild_id: int, session):
    return session.query(WatchLists).get(guild_id)


def update_server_channel(interaction: Interaction, session, status=False):
    result = session.query(ServerConfigs).get(interaction.guild_id)

    if result == None:
        nchc = ServerConfigs(
            id=interaction.guild_id, name=interaction.guild.name, channel=interaction.channel_id, muted=status)
        session.add(nchc)
    else:
        result.channel = interaction.channel_id
    session.commit()


def is_ally_recorded(obj: str, session):
    result = None
    if obj.isdigit():
        result = session.query(Alliances).get(int(obj))
        return (True, True) if result != None else (False, True)
    else:
        result = session.query(Alliances).filter(or_(
            Alliances.name.ilike(obj), Alliances.ticker.ilike(obj))).all()
        return (True, len(result)) if result != None else (False, True)


def add_new_ally_by_id(ally_id: int, session):
    response = get(
        f"https://esi.evetech.net/latest/alliances/{ally_id}/?datasource=tranquility", timeout=.75)
    if response != None and response.status_code == 200:
        data = response.json()
        ally = Alliances(id=ally_id, name=data["name"], ticker=data["ticker"])
        session.add(ally)
        session.commit()
        return True
    return False


def is_corp_recorded(obj: str, session):
    result = None
    if obj.isdigit():
        result = session.query(Corporations).get(int(obj))
        return (True, True) if result != None else (False, True)

    elif result == None:
        result = session.query(Corporations).filter(or_(
            Corporations.name.ilike(obj), Corporations.ticker.ilike(obj))).all()
        return (True, len(result)) if result != None else (False, True)


def add_new_corp_by_id(corp_id: int, session):
    response = get(
        f"https://esi.evetech.net/latest/corporations/{corp_id}/?datasource=tranquility", timeout=.75)
    if response != None and response.status_code == 200:
        data = response.json()
        alliance_id = data["alliance_id"] if "alliance_id" in data.keys(
        ) else None
        corp = Corporations(
            id=corp_id, alliance_id=alliance_id, name=data["name"], ticker=data["ticker"])
        session.add(corp)
        session.commit()
        return True
    return False


def add_object_to_watch(interaction: Interaction, session, obj: str, db_class, friend=None):
    guild_id = interaction.guild_id
    if not is_server_channel_set(guild_id, session):
        update_server_channel(interaction, session)

    reference = None
    if obj.isdigit():
        reference = session.query(db_class).get(int(obj))
    elif db_class is Alliances:
        reference = session.query(Alliances).filter(
            or_(Alliances.name.ilike(obj), Alliances.ticker.ilike(obj))).first()
    elif db_class is Corporations:
        reference = session.query(Corporations).filter(
            or_(Corporations.name.ilike(obj), Corporations.ticker.ilike(obj))).first()
    else:
        reference = session.query(db_class).filter(
            db_class.name.ilike(obj)).first()

    if reference == None:
        return False, False, "", False

    new = False
    watchl = does_server_have_filter(guild_id, session)
    if watchl == None:
        new = True
        watchl = WatchLists(server_id=guild_id, systems="[]", constellations="[]",
                            regions="[]", alliances="[]", corporations="[]",
                            f_corporations="[]", f_alliances="[]")

    ref_json = None
    f_json = None
    if db_class is Alliances:
        f_json = loads(watchl.f_alliances) if friend != None else None
        ref_json = loads(watchl.alliances)
    elif db_class is Corporations:
        f_json = loads(watchl.f_corporations) if friend != None else None
        ref_json = loads(watchl.corporations)
    elif db_class is Regions:
        ref_json = loads(watchl.regions)
    elif db_class is Constellations:
        ref_json = loads(watchl.constellations)
    elif db_class is Systems:
        ref_json = loads(watchl.systems)

    already_watched = False
    if reference.id not in ref_json:
        ref_json.append(reference.id)
    else:
        already_watched = True

    same_ally = True
    if friend != None:
        if reference.id not in f_json:
            f_json.append(reference.id)
            same_ally = False

    if db_class is Alliances:
        if friend != None:
            watchl.f_alliances = dumps(f_json)
        watchl.alliances = dumps(ref_json)
    elif db_class is Corporations:
        if friend != None:
            watchl.f_corporations = dumps(f_json)
        watchl.corporations = dumps(ref_json)
    elif db_class is Regions:
        watchl.regions = dumps(ref_json)
    elif db_class is Constellations:
        watchl.constellations = dumps(ref_json)
    elif db_class is Systems:
        watchl.systems = dumps(ref_json)

    if new:
        session.add(watchl)
    session.commit()

    return True, already_watched, reference.name, same_ally


def remove_object_from_watch(interaction: Interaction, session, obj: str, db_class):
    guild_id = interaction.guild_id
    if not is_server_channel_set(guild_id, session):
        update_server_channel(interaction, session)

    reference = None
    if obj.isdigit():
        reference = session.query(db_class).get(int(obj))
    elif db_class is Alliances:
        reference = session.query(Alliances).filter(
            or_(Alliances.name.ilike(obj), Alliances.ticker.ilike(obj))).first()
    elif db_class is Corporations:
        reference = session.query(Corporations).filter(
            or_(Corporations.name.ilike(obj), Corporations.ticker.ilike(obj))).first()
    else:
        reference = session.query(db_class).filter(
            db_class.name.ilike(obj)).first()

    if reference == None:
        return False, False, ""

    new = False
    watchl = does_server_have_filter(guild_id, session)
    if watchl == None:
        new = True
        watchl = WatchLists(server_id=guild_id, systems="[]", constellations="[]",
                            regions="[]", alliances="[]", corporations="[]",
                            f_alliances="[]", f_corporations="[]")

    ref_json = None
    f_json = None
    if db_class is Systems:
        ref_json = loads(watchl.systems)
    elif db_class is Constellations:
        ref_json = loads(watchl.constellations)
    elif db_class is Regions:
        ref_json = loads(watchl.regions)
    elif db_class is Corporations:
        ref_json = loads(watchl.corporations)
        f_json = loads(watchl.f_corporations)
    elif db_class is Alliances:
        ref_json = loads(watchl.alliances)
        f_json = loads(watchl.f_alliances)

    if reference.id not in ref_json:
        return False, True, reference.name
    else:
        ref_json.remove(reference.id)
    if f_json != None and reference.id in f_json:
        f_json.remove(reference.id)

    if db_class is Systems:
        watchl.systems = dumps(ref_json)
    elif db_class is Constellations:
        watchl.constellations = dumps(ref_json)
    elif db_class is Regions:
        watchl.regions = dumps(ref_json)
    elif db_class is Corporations:
        if f_json != None:
            watchl.f_corporations = dumps(f_json)
        watchl.corporations = dumps(ref_json)
    elif db_class is Alliances:
        if f_json != None:
            watchl.f_alliances = dumps(f_json)
        watchl.alliances = dumps(ref_json)

    if new:
        session.add(watchl)
    session.commit()

    return True, False, reference.name
