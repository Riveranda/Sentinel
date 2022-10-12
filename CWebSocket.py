from json import loads
from concurrent.futures import ThreadPoolExecutor
from dbutility import does_server_have_filter
from Schema import Corporations, Alliances, WatchLists, Constellations, Systems
import requests
import websocket
import time

message_queue = []


def check_for_unique_corp_ids(json_obj, session):
    ids = set()
    if "corporation_id" in json_obj["victim"]:
        ids.add(json_obj["victim"]["corporation_id"])
    for attacker in json_obj["attackers"]:
        if "corporation_id" in attacker:
            ids.add(attacker["corporation_id"])
    for row in session.query(Corporations).filter(Corporations.id.in_(ids)).all():
        ids.remove(row.id)

    if len(ids) == 0:
        return
    corp_dict = {}

    def get_corp_data_from_id(id: int):
        response = requests.get(
            f"https://esi.evetech.net/latest/corporations/{id}/?datasource=tranquility", timeout=.75)
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


def check_for_unique_ally_ids(json_obj, session):
    ids = set()
    if "alliance_id" in json_obj["victim"]:
        ids.add(json_obj["victim"]["alliance_id"])
    for attacker in json_obj["attackers"]:
        if "alliance_id" in attacker:
            ids.add(attacker["alliance_id"])
    for row in session.query(Alliances).filter(Alliances.id.in_(ids)).all():
        ids.remove(row.id)

    if len(ids) == 0:
        return

    ally_dict = {}

    def get_ally_data_from_id(id: int):
        response = requests.get(
            f"https://esi.evetech.net/latest/alliances/{id}/?datasource=tranquility", timeout=.75)
        if response != None and response.status_code == 200:
            ally_dict[id] = response.json()

    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(get_ally_data_from_id, ids)

    for key, value in ally_dict.items():
        alliance = Alliances(
            id=key, name=value["name"], ticker=value["ticker"])
        session.add(alliance)
    session.commit()


def does_msg_match_guild_watchlist(kill_obj, guild_id: int, session):
    filter = does_server_have_filter(guild_id, session)
    if filter == None:
        filter = WatchLists(server_id=guild_id)
        session.add(filter)
        session.commit()
        return True

    system_j = loads(filter.systems)
    f_count = len(system_j)
    if "solar_system_id" in kill_obj.keys() and kill_obj["solar_system_id"] in system_j:
        return True

    regions_j = loads(filter.regions)
    f_count += len(regions_j)
    for region in regions_j:
        const_id = session.query(Systems).get(
            kill_obj["solar_system_id"]).constellation_id
        region_id = session.query(Constellations).get(const_id).region_id
        if region == region_id:
            return True

    const_j = loads(filter.constellations)
    f_count += len(const_j)
    for const in const_j:
        const_id = session.query(Systems).get(
            kill_obj["solar_system_id"]).constellation_id
        if const == const_id:
            return True

    corp_j = loads(filter.corporations)
    ally_j = loads(filter.alliances)
    f_count += len(corp_j) + len(ally_j)

    if f_count == 0:
        return True

    if "corporation_id" in kill_obj["victim"] and kill_obj["victim"]["corporation_id"] in corp_j:
        return True
    if "alliance_id" in kill_obj["victim"] and kill_obj["victim"]["alliance_id"] in corp_j:
        return True

    if "attackers" in kill_obj:
        for attacker in kill_obj["attackers"]:
            if "corporation_id" in attacker and attacker["corporation_id"] in corp_j:
                return True
            if "alliance_id" in attacker and attacker["alliance_id"] in ally_j:
                return True
    return False


kill_counter = 0


def on_message(ws, message):
    global kill_counter
    kill_counter += 1
    print(f"Kill recieved {kill_counter}")

    from commands import Session
    json_obj = loads(message)
    session = Session()
    message_queue.append(json_obj)
    check_for_unique_corp_ids(json_obj, session)
    check_for_unique_ally_ids(json_obj, session)
    Session.remove()


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
