from json import loads, dumps
from concurrent.futures import ThreadPoolExecutor
from Dbutily import does_server_have_filter
from Schema import Corporations, Alliances, Regions, ServerConfigs, WatchLists, Constellations, Systems
from sqlalchemy.orm import sessionmaker
import requests
import websocket
import time

message_queue = []


def check_for_unique_corp_ids(json_obj, session):
    ids = []
    ids.append(json_obj["victim"]["corporation_id"])
    for attacker in json_obj["attackers"]:
        ids.append(attacker["corporation_id"])
    for id in ids:
        result = session.query(Corporations).get(id)
        if result != None:
            ids.remove(id)

    if len(ids) == 0:
        return

    corp_dict = {}

    def get_corp_data_from_id(id: int):
        response = requests.get(
            f"https://esi.evetech.net/latest/corporations/{id}/?datasource=tranquility")
        if response != None:
            corp_dict[id] = response.json()

    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(get_corp_data_from_id, ids)
    for key, value in corp_dict.items():
        alliance_id = None
        if "alliance_id" in value.keys():
            alliance_id = value["alliance_id"]
        corp = Corporations(
            id=key, name=value["name"], alliance_id=alliance_id)
        session.add(corp)
    session.commit()


def check_for_unique_ally_ids(json_obj, session):
    ids = []
    ids.append(json_obj["victim"]["alliance_id"])
    for attacker in json_obj["attackers"]:
        ids.append(attacker["alliance_id"])
    for id in ids:
        result = session.query(Alliances).get(id)
        if result != None:
            ids.remove(id)

    if len(ids) == 0:
        return

    ally_dict = {}

    def get_ally_data_from_id(id: int):
        response = requests.get(
            f"https://esi.evetech.net/latest/alliances/{id}/?datasource=tranquility")
        if response != None:
            ally_dict[id] = response.json()

    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(get_ally_data_from_id, ids)

    for key, value in ally_dict.items():
        alliance = Alliances(id=key, name=value["name"])
        session.add(alliance)
    session.commit()


def does_msg_match_guild_watchlist(kill_obj, guild_id: int, session):
    filter = None
    if not does_server_have_filter(session, guild_id):
        filter = WatchLists(server_id=guild_id)
        session.add(filter)
        session.commit()
        return True
    else:
        filter = session.query(WatchLists).get(guild_id)

    if filter == None:
        return True
    if len(filter.systems) == 0 and len(filter.constellations) == 0 and len(filter.regions) == 0 and len(filter.corporations) == 0 and len(filter.alliances) == 0:
        return True

    system_j = loads(filter.systems)
    if kill_obj["solar_system_id"] in system_j:
        return True

    regions_j = loads(filter.regions)
    for region in regions_j:
        const_id = session.query(Systems).get(
            kill_obj["solar_system_id"]).constellation_id
        region_id = session.query(Constellations).get(const_id).region_id
        if region == region_id:
            return True

    const_j = loads(filter.constellations)
    for const in const_j:
        const_id = session.query(Systems).get(
            kill_obj["solar_system_id"]).constellation_id
        if const == const_id:
            return True

    corp_j = loads(filter.corporations)
    ally_j = loads(filter.alliances)
    if len(corp_j) == 0 and len(ally_j) == 0:
        return False
    if "corporation_id" in kill_obj["victim"] and kill_obj["victim"]["corporation_id"] in corp_j:
        return True
    if "alliance_id" in kill_obj["victim"] and kill_obj["victim"]["alliance_id"] in corp_j:
        return True

    if "attackers" in attacker:
        for attacker in kill_obj["attackers"]:
            if "corporation_id" in attacker and attacker["corporation_id"] in corp_j:
                return True
            if "alliance_id" in attacker and attacker["alliance_id"] in ally_j:
                return True
    return False


def on_message(ws, message):
    from main import engine
    Session = sessionmaker(bind=engine)
    session = Session()

    json_obj = loads(message)
    print("Kill recieved")

    message_queue.append(json_obj)
    check_for_unique_corp_ids(json_obj, session)
    check_for_unique_ally_ids(json_obj, session)
    #print(dumps(loads(message), indent=4))


def on_error(ws, error):
    time.sleep(5)
    initialize_websocket()


def on_close(ws):
    print("Closed")


def on_open(ws):
    ws.send('{"action":"sub","channel":"killstream"}')


def initialize_websocket():

    ws = websocket.WebSocketApp("wss://zkillboard.com/websocket/",
                                on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.run_forever()
