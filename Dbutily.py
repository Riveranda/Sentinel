
from functools import lru_cache
from Schema import *
import json


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


# # TODO: After production cleanup unecessary existence checks since create_new_guild was added!
# def add_corp_to_watch(guild_id: int, ctx, session, obj: str):
#     if not is_server_channel_set(session, guild_id):
#         update_server_channel(session, ctx)

#     region = session.query(Regions).get(int(obj)) if obj.isdigit(
#     ) else session.query(Regions).filter(Regions.name.ilike(obj)).first()

#     if region == None:
#         return False, False, ""

#     watchl = None
#     add = False
#     if does_server_have_filter(session, guild_id):
#         watchl = session.query(WatchLists).get(guild_id)
#     else:
#         add = True
#         watchl = WatchLists(server_id=guild_id, regions="[]")

#     regions_json = json.loads(watchl.regions)

#     already_watched = False
#     if region.name not in regions_json:
#         regions_json.append(region.name)
#     else:
#         already_watched = True

#     watchl.regions = json.dumps(regions_json)
#     if add:
#         session.add(watchl)
#     session.commit()

#     return True, already_watched, region.name

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

    if region.name not in regions_json:
        return False, True, region.name
    else:
        regions_json.remove(region.name)

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
    if region.name not in regions_json:
        regions_json.append(region.name)
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

    if constellation.name not in constellations_json:
        return False, True, constellation.name
    else:
        constellations_json.remove(constellation.name)

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
    if constellation.name not in constellations_json:
        constellations_json.append(constellation.name)
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

    if system.name not in systems_json:
        return False, True, system.name
    else:
        systems_json.remove(system.name)

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
    if system.name not in systems_json:
        systems_json.append(system.name)
    else:
        already_watched = True

    watchl.systems = json.dumps(systems_json)
    if add:
        session.add(watchl)
    session.commit()

    return True, already_watched, system.name
