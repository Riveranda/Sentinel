
from functools import lru_cache
from Schema import *
import json
import requests


@lru_cache(maxsize=50)
def is_server_channel_set(session, id: int):
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

def set_filter_to_all(guild_id : int, session):
    if not does_server_have_filter():
        filter = WatchLists(server_id=guild_id)
        session.add(filter)
    else:
        filter = session.query(WatchLists).get(guild_id)
        filter.systems = "[]"
        filter.constellations="[]"
        filter.regions="[]"
        filter.corporations="[]"
        filter.alliances="[]"
        filter.players="[]"
    session.commit()


def get_channel_id_from_guild_id(session, id: int):
    return session.query(ServerConfigs).get(id).channel


def update_server_muted(session, ctx, status: bool):
    results = session.query(ServerConfigs).get(ctx.guild.id)
    if results == None:
        update_server_channel(session, ctx, status=status)
    else:
        results.muted = status
        session.commit()


def is_server_muted(session, id: int):
    result = session.query(ServerConfigs).get(id)
    if result != None:
        return result.muted
    return True


def does_server_have_filter(session, guild_id: int):
    result = session.query(WatchLists).get(guild_id)
    return not result == None


def update_server_channel(session, ctx, status=False):
    result = session.query(ServerConfigs).get(ctx.guild.id)
    if result == None:
        nchc = ServerConfigs(
            id=ctx.guild.id, name=ctx.guild.name, channel=ctx.channel.id, muted=status)
        session.add(nchc)
    else:
        result.channel = ctx.channel.id
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
    response = requests.get(
        f"https://esi.evetech.net/latest/alliances/{id}/?datasource=tranquility")
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
    response = requests.get(
        f"https://esi.evetech.net/latest/corporations/{id}/?datasource=tranquility")
    if response != None and response.status_code == 200:
        data = response.json()
        corp = Corporations(
            id=corp_id, alliance_id=data["alliance_id"], name=data["name"])
        session.add(corp)
        session.commit()

# TODO: After production cleanup unecessary existence checks since create_new_guild was added!


def add_ally_to_watch(guild_id: int, ctx, session, obj: str):
    if not is_server_channel_set(session, guild_id):
        update_server_channel(session, ctx)

    ally = session.query(Alliances).get(int(obj)) if obj.isdigit(
    ) else session.query(Alliances).filter(Alliances.name.ilike(obj)).first()

    if ally == None:
        return False, False, ""

    watchl = None
    add = False
    if does_server_have_filter(session, guild_id):
        watchl = session.query(WatchLists).get(guild_id)
    else:
        add = True
        watchl = WatchLists(server_id=guild_id, alliances="[]")

    ally_json = json.loads(watchl.alliances)

    already_watched = False
    if ally.id not in ally_json:
        ally_json.append(ally.id)
    else:
        already_watched = True

    watchl.alliances = json.dumps(ally_json)
    if add:
        session.add(watchl)
    session.commit()

    return True, already_watched, ally.name

# TODO: After production cleanup unecessary existence checks since create_new_guild was added!


def remove_ally_from_watch(guild_id: int, ctx, session, obj: str):
    if not is_server_channel_set(session, guild_id):
        update_server_channel(session, ctx)

    ally = session.query(Alliances).get(int(obj)) if obj.isdigit(
    ) else session.query(Alliances).filter(Alliances.name.ilike(obj)).first()

    if ally == None:
        return False, False, ""

    watchl = None
    new = False
    if does_server_have_filter(session, guild_id):
        watchl = session.query(WatchLists).get(guild_id)
    else:
        new = True
        watchl = WatchLists(server_id=guild_id)

    ally_json: list = json.loads(watchl.alliances)

    if ally.id not in ally_json:
        return False, True, ally.id
    else:
        ally_json.remove(ally.id)

    watchl.alliances = json.dumps(ally_json)

    if new:
        session.add(watchl)
    session.commit()

    return True, False, ally.name

# TODO: After production cleanup unecessary existence checks since create_new_guild was added!


def add_corp_to_watch(guild_id: int, ctx, session, obj: str):
    if not is_server_channel_set(session, guild_id):
        update_server_channel(session, ctx)

    corp = session.query(Corporations).get(int(obj)) if obj.isdigit(
    ) else session.query(Corporations).filter(Corporations.name.ilike(obj)).first()

    if corp == None:
        return False, False, ""

    watchl = None
    add = False
    if does_server_have_filter(session, guild_id):
        watchl = session.query(WatchLists).get(guild_id)
    else:
        add = True
        watchl = WatchLists(server_id=guild_id, corporations="[]")

    corps_json = json.loads(watchl.corporations)

    already_watched = False
    if corp.id not in corps_json:
        corps_json.append(corp.id)
    else:
        already_watched = True

    watchl.corporations = json.dumps(corps_json)
    if add:
        session.add(watchl)
    session.commit()

    return True, already_watched, corp.name


def remove_corp_from_watch(guild_id: int, ctx, session, obj: str):
    if not is_server_channel_set(session, guild_id):
        update_server_channel(session, ctx)

    corp = session.query(Corporations).get(int(obj)) if obj.isdigit(
    ) else session.query(Corporations).filter(Corporations.name.ilike(obj)).first()

    if corp == None:
        return False, False, ""

    watchl = None
    new = False
    if does_server_have_filter(session, guild_id):
        watchl = session.query(WatchLists).get(guild_id)
    else:
        new = True
        watchl = WatchLists(server_id=guild_id)

    corps_json: list = json.loads(watchl.corporations)

    if corp.id not in corps_json:
        return False, True, corp.id
    else:
        corps_json.remove(corp.id)

    watchl.corporations = json.dumps(corps_json)

    if new:
        session.add(watchl)
    session.commit()

    return True, False, corp.name

# TODO: After production cleanup unecessary existence checks since create_new_guild was added!


def remove_region_from_watch(guild_id: int, ctx, session, obj: str):
    if not is_server_channel_set(session, guild_id):
        update_server_channel(session, ctx)

    region = session.query(Regions).get(int(obj)) if obj.isdigit(
    ) else session.query(Regions).filter(Regions.name.ilike(obj)).first()

    if region == None:
        return False, False, ""

    watchl = None
    new = False
    if does_server_have_filter(session, guild_id):
        watchl = session.query(WatchLists).get(guild_id)
    else:
        new = True
        watchl = WatchLists(server_id=guild_id)

    regions_json: list = json.loads(watchl.regions)

    if region.id not in regions_json:
        return False, True, region.id
    else:
        regions_json.remove(region.id)

    watchl.regions = json.dumps(regions_json)

    if new:
        session.add(watchl)
    session.commit()

    return True, False, region.name

# TODO: After production cleanup unecessary existence checks since create_new_guild was added!


def add_region_to_watch(guild_id: int, ctx, session, obj: str):
    if not is_server_channel_set(session, guild_id):
        update_server_channel(session, ctx)

    region = session.query(Regions).get(int(obj)) if obj.isdigit(
    ) else session.query(Regions).filter(Regions.name.ilike(obj)).first()

    if region == None:
        return False, False, ""

    watchl = None
    add = False
    if does_server_have_filter(session, guild_id):
        watchl = session.query(WatchLists).get(guild_id)
    else:
        add = True
        watchl = WatchLists(server_id=guild_id, regions="[]")

    regions_json = json.loads(watchl.regions)

    already_watched = False
    if region.id not in regions_json:
        regions_json.append(region.id)
    else:
        already_watched = True

    watchl.regions = json.dumps(regions_json)
    if add:
        session.add(watchl)
    session.commit()

    return True, already_watched, region.name

# TODO: After production cleanup unecessary existence checks since create_new_guild was added!


def remove_constellation_from_watch(guild_id: int, ctx, session, obj: str):
    if not is_server_channel_set(session, guild_id):
        update_server_channel(session, ctx)

    constellation = session.query(Constellations).get(int(obj)) if obj.isdigit(
    ) else session.query(Constellations).filter(Constellations.name.ilike(obj)).first()

    if constellation == None:
        return False, False, ""

    watchl = None
    new = False
    if does_server_have_filter(session, guild_id):
        watchl = session.query(WatchLists).get(guild_id)
    else:
        new = True
        watchl = WatchLists(server_id=guild_id)

    constellations_json: list = json.loads(watchl.constellations)

    if constellation.id not in constellations_json:
        return False, True, constellation.id
    else:
        constellations_json.remove(constellation.id)

    watchl.constellations = json.dumps(constellations_json)

    if new:
        session.add(watchl)
    session.commit()

    return True, False, constellation.name

# TODO: After production cleanup unecessary existence checks since create_new_guild was added!


def add_constellation_to_watch(guild_id: int, ctx, session, obj: str):
    if not is_server_channel_set(session, guild_id):
        update_server_channel(session, ctx)

    constellation = session.query(Constellations).get(int(obj)) if obj.isdigit(
    ) else session.query(Constellations).filter(Constellations.name.ilike(obj)).first()

    if constellation == None:
        return False, False, ""

    watchl = None
    add = False
    if does_server_have_filter(session, guild_id):
        watchl = session.query(WatchLists).get(guild_id)
    else:
        add = True
        watchl = WatchLists(server_id=guild_id, constellations="[]")

    constellations_json = json.loads(watchl.constellations)

    already_watched = False
    if constellation.id not in constellations_json:
        constellations_json.append(constellation.id)
    else:
        already_watched = True

    watchl.constellations = json.dumps(constellations_json)
    if add:
        session.add(watchl)
    session.commit()

    return True, already_watched, constellation.name

# TODO: After production cleanup unecessary existence checks since create_new_guild was added!


def remove_system_from_watch(guild_id: int, ctx, session, obj: str):
    if not is_server_channel_set(session, guild_id):
        update_server_channel(session, ctx)

    system = session.query(Systems).get(int(obj)) if obj.isdigit(
    ) else session.query(Systems).filter(Systems.name.ilike(obj)).first()

    if system == None:
        return False, False, ""

    watchl = None
    new = False
    if does_server_have_filter(session, guild_id):
        watchl = session.query(WatchLists).get(guild_id)
    else:
        new = True
        watchl = WatchLists(server_id=guild_id)

    systems_json: list = json.loads(watchl.systems)

    if system.id not in systems_json:
        return False, True, system.id
    else:
        systems_json.remove(system.id)

    watchl.systems = json.dumps(systems_json)

    if new:
        session.add(watchl)
    session.commit()

    return True, False, system.name

# TODO: After production cleanup unecessary existence checks since create_new_guild was added!


def add_system_to_watch(guild_id: int, ctx, session, obj: str):
    if not is_server_channel_set(session, guild_id):
        update_server_channel(session, ctx)

    system = session.query(Systems).get(int(obj)) if obj.isdigit(
    ) else session.query(Systems).filter(Systems.name.ilike(obj)).first()

    if system == None:
        return False, False, ""

    watchl = None
    add = False
    if does_server_have_filter(session, guild_id):
        watchl = session.query(WatchLists).get(guild_id)
    else:
        add = True
        watchl = WatchLists(server_id=guild_id, systems="[]")

    systems_json = json.loads(watchl.systems)

    already_watched = False
    if system.id not in systems_json:
        systems_json.append(system.id)
    else:
        already_watched = True

    watchl.systems = json.dumps(systems_json)
    if add:
        session.add(watchl)
    session.commit()

    return True, already_watched, system.name
