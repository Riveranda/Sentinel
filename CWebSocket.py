from Schema import Corporations, Alliances, Constellations, ServerConfigs, Systems, Ships, Regions
from concurrent.futures import ThreadPoolExecutor
import websocket
from functools import lru_cache
from threading import Thread
from discord import Embed
from requests import get
from ujson import loads

message_queue = []


def check_for_unique_corp_ids(json_obj):
    from commands import Session
    session = Session()
    ids = set()
    if "corporation_id" in json_obj["victim"]:
        ids.add(json_obj["victim"]["corporation_id"])
    for attacker in json_obj["attackers"]:
        if "corporation_id" in attacker:
            ids.add(attacker["corporation_id"])
    for row in session.query(Corporations).filter(Corporations.id.in_(ids)).all():
        ids.remove(row.id)

    if len(ids) == 0:
        Session.remove()
        return
    corp_dict = {}

    def get_corp_data_from_id(id: int):
        response = get(
            f"https://esi.evetech.net/latest/corporations/{id}/?datasource=tranquility", timeout=.5)
        if response != None and response.status_code == 200:
            corp_dict[id] = response.json()

    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(get_corp_data_from_id, ids)

    for key, value in corp_dict.items():
        alliance_id = None
        if "alliance_id" in value.keys():
            alliance_id = value["alliance_id"]
        corp = Corporations(
            id=key, name=value["name"], alliance_id=alliance_id, ticker=value["ticker"])
        session.add(corp)
    session.commit()
    Session.remove()


def check_for_unique_ally_ids(json_obj):
    from commands import Session
    session = Session()
    ids = set()
    if "alliance_id" in json_obj["victim"]:
        ids.add(json_obj["victim"]["alliance_id"])
    for attacker in json_obj["attackers"]:
        if "alliance_id" in attacker:
            ids.add(attacker["alliance_id"])
    for row in session.query(Alliances).filter(Alliances.id.in_(ids)).all():
        ids.remove(row.id)

    if len(ids) == 0:
        Session.remove()
        return

    ally_dict = {}

    def get_ally_data_from_id(id: int):
        response = get(
            f"https://esi.evetech.net/latest/alliances/{id}/?datasource=tranquility", timeout=.5)
        if response != None and response.status_code == 200:
            ally_dict[id] = response.json()

    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(get_ally_data_from_id, ids)

    for key, value in ally_dict.items():
        alliance = Alliances(
            id=key, name=value["name"], ticker=value["ticker"])
        session.add(alliance)
    session.commit()
    Session.remove()


def get_ship_image(id: int):
    return f"https://images.evetech.net/types/{id}/icon"


def check_for_unique_ship_ids(json_obj):
    from commands import Session
    session = Session()
    ids = set()
    if "ship_type_id" in json_obj["victim"]:
        ids.add(json_obj["victim"]["ship_type_id"])
    if "attackers" in json_obj:
        for attacker in json_obj["attackers"]:
            if "ship_type_id" in attacker:
                ids.add(attacker["ship_type_id"])
    for row in session.query(Ships).filter(Ships.id.in_(ids)).all():
        ids.remove(row.id)

    if len(ids) == 0:
        Session.remove()
        return

    ship_dict = {}

    def get_ship_data_from_id(id: int):
        response = get(
            f"https://esi.evetech.net/latest/universe/types/{id}/?datasource=tranquility&language=en", timeout=.5)
        if response != None and response.status_code == 200:
            ship_dict[id] = response.json()

    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(get_ship_data_from_id, ids)

    for key, value in ship_dict.items():
        ship = Ships(
            id=key, name=value["name"], group_id=value["group_id"])
        session.add(ship)
    session.commit()
    Session.remove()


@lru_cache(maxsize=20)
def get_ship_name(id: int, session):
    result = session.query(Ships).get(id)
    return result.name if result != None else "NULL"


@lru_cache(maxsize=20)
def get_system_and_region_names(id: int, session):
    system = session.query(Systems).get(id)
    constellation = session.query(Constellations).get(system.constellation_id)
    region = session.query(Regions).get(constellation.region_id)
    return (system.name, region.name)


@lru_cache(maxsize=20)
def get_corporation_data(id: int, session):
    corp_name = session.query(Corporations).get(id).name
    corp_logo = f"https://images.evetech.net/corporations/{id}/logo/"
    corp_link = f"https://zkillboard.com/corporation/{id}/"
    return corp_name, corp_logo, corp_link


@lru_cache(maxsize=20)
def get_alliance_data(id: int, session):
    ally_name = session.query(Alliances).get(id).name
    ally_link = f"https://zkillboard.com/alliance/{id}/"
    return ally_name, ally_link


title_start_map = {True: "Kill: ", False: "Loss: ", None: ""}


@lru_cache(maxsize=20)
def get_ship_data(id: int):
    response = get(
        f"https://esi.evetech.net/latest/universe/types/{id}/?datasource=tranquility&language=en", timeout=.5)
    if response != None and response.status_code == 200:
        jobj = response.json()
        return jobj["name"], f"https://zkillboard.com/ship/{id}/"


@lru_cache(maxsize=20)
def get_pilot_name(id: int):
    response = get(
        f"https://esi.evetech.net/latest/characters/{id}/?datasource=tranquility&language=en", timeout=.5)
    if response != None and response.status_code == 200:
        jobj = response.json()
        return jobj["name"]


def generate_embed(kill_obj, status: bool, filter, session):
    embed = Embed()

    color_map = {True: 0x33FF57, False: 0xfa0505, None: 0xB82AF1}

    config = session.query(ServerConfigs).get(filter.server_id)
    if config.neutral_color != None:
        color_map[None] = int(config.neutral_color, base=16)
    embed.color = color_map[status]

    title_start: str = title_start_map[status]
    victim_ship_id = kill_obj["victim"]["ship_type_id"]

    if status == True and kill_obj["zkb"]["awox"] == True:
        title_start = "Friendly Fire: "

    embed.set_thumbnail(url=get_ship_image(victim_ship_id))

    system_name, region_name = get_system_and_region_names(
        kill_obj['solar_system_id'], session)
    embed.title = f"{title_start}{get_ship_name(victim_ship_id, session)} destroyed in {system_name} ({region_name})"

    embed.url = kill_obj["zkb"]["url"]

    damage_embed_str = f"Destroyed: {'{:,.2f}'.format(kill_obj['zkb']['destroyedValue'])} isk\n"
    damage_embed_str += f"Dropped: {'{:,.2f}'.format(kill_obj['zkb']['droppedValue'])} isk\n"
    damage_embed_str += f"Total: {'{:,.2f}'.format(kill_obj['zkb']['totalValue'])} isk"

    embed.add_field(name="Damages", value=damage_embed_str, inline=False)

    ids = {}

    if "character_id" in kill_obj["victim"]:
        ids[True] = kill_obj["victim"]["character_id"]

    pilot_names = {}
    killer = None

    def set_names(item: dict):
        key, value = item
        if key == True:
            pilot_names["victim"] = get_pilot_name(value)
        else:
            pilot_names["killer"] = get_pilot_name(value)
    if "attackers" in kill_obj:
        for attacker in kill_obj["attackers"]:
            if attacker["final_blow"] == True:
                killer = attacker
                if "character_id" in attacker:
                    ids[False] = attacker["character_id"]

    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(set_names, ids.items())

    victim_embed_str = f"Ship: [{get_ship_name(victim_ship_id, session)}](https://zkillboard.com/ship/{victim_ship_id})"
    if True in ids and "victim" in pilot_names:
        victim_embed_str += f"\nPilot: [{pilot_names['victim']}](https://zkillboard.com/character/{ids[True]})"

    if "corporation_id" in kill_obj["victim"]:
        corp_name, corp_logo, corp_link = get_corporation_data(
            kill_obj["victim"]["corporation_id"], session)
        victim_embed_str += f"\nCorp: [{corp_name}]({corp_link})"
        embed.set_author(name=corp_name,
                         icon_url=corp_logo, url=corp_link)

    if "alliance_id" in kill_obj["victim"]:
        ally_name, ally_link = get_alliance_data(
            kill_obj["victim"]["alliance_id"], session)
        victim_embed_str += f"\nAlliance: [{ally_name}]({ally_link})"
    embed.add_field(
        name="Victim", value=victim_embed_str, inline=True)

    if killer != None:
        if "ship_type_id" in killer:
            try:
                killer_ship_id = killer["ship_type_id"]
                finalblow_embed_str = f"Ship: [{get_ship_name(killer_ship_id, session)}](https://zkillboard.com/ship/{killer_ship_id})"
            except Exception as e:
                from main import logger
                logger.exception(e)
                print(e)
        if False in ids and "killer" in pilot_names:
            finalblow_embed_str += f"\nPilot: [{pilot_names['killer']}](https://zkillboard.com/character/{ids[False]})"
        if "corporation_id" in killer:
            corp_name, corp_logo, corp_link = get_corporation_data(
                killer["corporation_id"], session)
            finalblow_embed_str += f"\nCorp: [{corp_name}]({corp_link})"
        if "alliance_id" in killer:
            ally_name, ally_link = get_alliance_data(
                killer["alliance_id"], session)
            finalblow_embed_str += f"\nAlliance: [{ally_name}]({ally_link})"
    if "attackers" in kill_obj:
        embed.add_field(name="Final Blow",
                        value=finalblow_embed_str, inline=True)

    details_embed_str = f"System: [{system_name}](http://evemaps.dotlan.net/map/{region_name.replace(' ', '_')}/{system_name.replace(' ', '_')}/) ({region_name})"
    if "attackers" in kill_obj:
        details_embed_str += f"\nFleet Size : {len(kill_obj['attackers'])}"
    details_embed_str += f"\nKill Mail: [{get_ship_name(victim_ship_id, session)}]({kill_obj['zkb']['url']})"

    embed.add_field(name="Details", value=details_embed_str, inline=True)

    return embed


def does_msg_match_guild_watchlist(kill_obj, filter, session):
    try:
        system_j = loads(filter.systems)
        f_count = len(system_j)
        status = None

        corp_j = loads(filter.corporations)
        ally_j = loads(filter.alliances)

        fcorp_j = loads(filter.f_corporations)
        fally_j = loads(filter.f_alliances)
        f_count += len(corp_j) + len(ally_j)

        if "corporation_id" in kill_obj["victim"]:
            if kill_obj["victim"]["corporation_id"] in fcorp_j:
                status = False
                return True, generate_embed(kill_obj, status, filter, session)
            if kill_obj["victim"]["corporation_id"] in corp_j:
                return True, generate_embed(kill_obj, status, filter, session)

        if "alliance_id" in kill_obj["victim"]:
            if kill_obj["victim"]["alliance_id"] in fally_j:
                status = False
                return True, generate_embed(kill_obj, status, filter, session)
            if kill_obj["victim"]["alliance_id"] in corp_j:
                return True, generate_embed(kill_obj, status, filter, session)

        if "attackers" in kill_obj:
            for attacker in kill_obj["attackers"]:
                if "corporation_id" in attacker:
                    if attacker["corporation_id"] in fcorp_j:
                        status = True
                        return True, generate_embed(kill_obj, status, filter, session)
                    if attacker["corporation_id"] in corp_j:
                        return True, generate_embed(kill_obj, status, filter, session)
                if "alliance_id" in attacker:
                    if attacker["alliance_id"] in fally_j:
                        status = True
                        return True, generate_embed(kill_obj, status, filter, session)
                    if attacker["alliance_id"] in ally_j:
                        return True, generate_embed(kill_obj, status, filter, session)

        if "solar_system_id" in kill_obj.keys() and kill_obj["solar_system_id"] in system_j:
            return True, generate_embed(kill_obj, status, filter, session)

        regions_j = loads(filter.regions)
        f_count += len(regions_j)
        for region in regions_j:
            const_id = session.query(Systems).get(
                kill_obj["solar_system_id"]).constellation_id
            region_id = session.query(Constellations).get(const_id).region_id
            if region == region_id:
                return True, generate_embed(kill_obj, status, filter, session)

        const_j = loads(filter.constellations)
        f_count += len(const_j)
        if f_count == 0:
            return True, generate_embed(kill_obj, status, filter, session)

        for const in const_j:
            const_id = session.query(Systems).get(
                kill_obj["solar_system_id"]).constellation_id
            if const == const_id:
                return True, generate_embed(kill_obj, status, filter, session)
    except Exception as e:
        from main import logger
        from gc import collect
        collect()
        logger.debug(f"Error in does_msg_match_guild_watchlist: {e}")
    return False, None


kill_counter = 0


def on_message(ws, message):
    try:
        global kill_counter
        kill_counter += 1
        print(f"Kill recieved {kill_counter}")

        json_obj = loads(message)

        threads = []
        threads.append(Thread(target=check_for_unique_corp_ids,
                              args=(json_obj,)))

        threads.append(Thread(target=check_for_unique_ally_ids,
                              args=(json_obj,)))

        threads.append(Thread(target=check_for_unique_ship_ids,
                              args=(json_obj,)))
        for t in threads:
            t.start()

        for t in threads:
            t.join()

        message_queue.append(json_obj)
    except Exception as e:
        from main import logger
        from gc import collect
        collect()
        logger.exception(e)


def on_error(ws, error):
    from main import logger
    logger.exception(error)


def on_close(ws):
    print("Closed")


def on_open(ws):
    ws.send('{"action":"sub","channel":"killstream"}')


def initialize_websocket():
    from time import sleep
    from main import logger
    from gc import collect
    
    while True:
        try: 
            websocket.enabletrace(False)
            ws = websocket.WebSocketApp("wss://zkillboard.com/websocket/",
                            on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
            ws.run_forever(skip_utf8_validation=True, ping_interval=10, ping_timeout=8)
        except Exception as e:
            collect()
            logger.debug(f"Websocket connection Error  : {e}")
        logger.debug("Reconnecting websocket  after 5 sec")
        sleep(5)
            
