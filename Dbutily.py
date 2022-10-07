
from functools import lru_cache
from Schema import *

@lru_cache(maxsize=50)
def is_server_channel_set(session, id: int):
    result = session.query(ServerConfigs).get(id)
    if result != None:
        return not result.channel == None
    return False

def get_channel_id_from_guild_id(session, id: int):
    return session.query(ServerConfigs).get(id).channel

def update_server_muted(session, ctx, status: bool):
    results = session.query(ServerConfigs).get(ctx.guild.id)
    if results == None:
        update_server_channel(session, ctx, status=status)
    else:
        results.muted = status
        session.commit()

def is_server_muted(session, id:int):
    result = session.query(ServerConfigs).get(id)
    if result != None:
        return result.muted
    return True

def update_server_channel(session, ctx, status=False):
    result = session.query(ServerConfigs).get(ctx.guild.id)
    if result == None:
        nchc = ServerConfigs(
            id=ctx.guild.id, name=ctx.guild.name, channel=ctx.channel.id, muted=status)
        session.add(nchc)
    else:
        result.channel = ctx.channel.id
    session.commit()

def is_system_being_watched(session, guild_id: int, system_id: int):
    result = session.query(WatchList).filter(WatchList.server_id == guild_id, WatchList.system_id == system_id)
    return not (result == None)

def add_system_to_watch(session, ctx, system: str):
    result = session.query(WatchList).filter(WatchList.server_id == ctx.guild.id, Systems.name == system.lower())
    
    if result == None:

        return True
    else:
        return False  


