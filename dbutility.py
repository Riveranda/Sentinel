
from functools import lru_cache
from schema import *
from orjson import loads, dumps
from requests import get
import discord


@lru_cache(maxsize=50)
def is_server_channel_set(id: int, session):
    result = session.query(ServerConfigs).get(id)
    if result != None:
        return not result.channel == None
    return False


def create_new_guild(channel_id: int, guild, session):
    result = session.query(ServerConfigs).get(guild.id)
    if result == None:
        config = ServerConfigs(id=guild.id, name=guild.name,
                               channel=channel_id, muted=False)
        session.add(config)
    result = session.query(WatchLists).get(guild.id)
    if result == None:
        wlist = WatchLists(server_id=guild.id)
        session.add(wlist)
    session.commit()


def set_filter_to_all(guild_id: int, session):
    if not does_server_have_filter(guild_id, session):
        filter = WatchLists(server_id=guild_id)
        session.add(filter)
    else:
        filter = session.query(WatchLists).get(guild_id)
        filter.systems = "[]"
        filter.constellations = "[]"
        filter.regions = "[]"
        filter.corporations = "[]"
        filter.alliances = "[]"
        filter.players = "[]"
    session.commit()


def get_channel_id_from_guild_id(session, id: int):
    return session.query(ServerConfigs).get(id).channel


def update_server_muted(session, interaction, status: bool):
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
    result = session.query(WatchLists).get(guild_id)
    return not result == None


def update_server_channel(interaction: discord.Interaction, session, status=False):
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
    else:
        result = session.query(Alliances).filter(
            Alliances.name.ilike(obj)).first()
    return not result == None


def add_new_ally_by_id(ally_id: int, session):
    response = get(
        f"https://esi.evetech.net/latest/alliances/{ally_id}/?datasource=tranquility")
    if response != None and response.status_code == 200:
        data = response.json()
        ally = Alliances(id=ally_id, name=data["name"])
        session.add(ally)
        session.commit()


def is_corp_recorded(obj: str, session):
    result = None
    if obj.isdigit():
        result = session.query(Corporations).get(int(obj))
    else:
        result = session.query(Corporations).filter(
            Corporations.name.ilike(obj)).first()
    return not result == None


def add_new_corp_by_id(corp_id: int, session):

    response = get(
        f"https://esi.evetech.net/latest/corporations/{corp_id}/?datasource=tranquility")
    if response != None and response.status_code == 200:
        data = response.json()
        alliance_id = data["alliance_id"] if "alliance_id" in data.keys(
        ) else None
        corp = Corporations(
            id=corp_id, alliance_id=alliance_id, name=data["name"])
        session.add(corp)
        session.commit()


def add_object_to_watch(interaction: discord.Interaction, session, obj: str, db_class):
    guild_id = interaction.guild_id
    if not is_server_channel_set(guild_id, session):
        update_server_channel(interaction, session)

    reference = session.query(db_class).get(int(obj)) if obj.isdigit(
    ) else session.query(db_class).filter(db_class.name.ilike(obj)).first()

    if reference == None:
        return False, False, ""

    watchl = None
    add = False
    if does_server_have_filter(guild_id, session):
        watchl = session.query(WatchLists).get(guild_id)
    else:
        add = True
        watchl = WatchLists(server_id=guild_id, systens="[]", constellations="[]",
                            regions="[]", alliances="[]", corporations="[]")

    ref_json = None
    if db_class is Alliances:
        ref_json = loads(watchl.alliances)
    elif db_class is Corporations:
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

    if db_class is Alliances:
        watchl.alliances = dumps(ref_json)
    elif db_class is Corporations:
        watchl.corporations = dumps(ref_json)
    elif db_class is Regions:
        watchl.regions = dumps(ref_json)
    elif db_class is Constellations:
        watchl.constellations = dumps(ref_json)
    elif db_class is Systems:
        watchl.systems = dumps(ref_json)

    if add:
        session.add(watchl)
    session.commit()

    return True, already_watched, reference.name


def remove_object_from_watch(interaction: discord.Interaction, session, obj: str, db_class):
    guild_id = interaction.guild_id
    if not is_server_channel_set(guild_id, session):
        update_server_channel(interaction, session)

    reference = session.query(db_class).get(int(obj)) if obj.isdigit(
    ) else session.query(db_class).filter(db_class.name.ilike(obj)).first()

    if reference == None:
        return False, False, ""

    watchl = None
    new = False
    if does_server_have_filter(guild_id, session):
        watchl = session.query(WatchLists).get(guild_id)
    else:
        new = True
        watchl = WatchLists(server_id=guild_id)

    ref_json = None
    if db_class is Systems:
        ref_json = loads(watchl.systems)
    elif db_class is Constellations:
        ref_json = loads(watchl.constellations)
    elif db_class is Regions:
        ref_json = loads(watchl.regions)
    elif db_class is Corporations:
        ref_json = loads(watchl.corporations)
    elif db_class is Alliances:
        ref_json = loads(watchl.alliances)

    if reference.id not in ref_json:
        return False, True, reference.id
    else:
        ref_json.remove(reference.id)

    if db_class is Systems:
        watchl.systems = dumps(ref_json)
    elif db_class is Constellations:
        watchl.constellations = dumps(ref_json)
    elif db_class is Regions:
        watchl.regions = dumps(ref_json)
    elif db_class is Corporations:
        watchl.corporations = dumps(ref_json)
    elif db_class is Alliances:
        watchl.alliances = dumps(ref_json)

    if new:
        session.add(watchl)
    session.commit()

    return True, False, reference.name
