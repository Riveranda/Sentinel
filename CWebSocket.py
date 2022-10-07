import websocket
import time
from json import loads
from concurrent.futures import ThreadPoolExecutor
from Schema import Corporations, Alliances
from sqlalchemy.orm import sessionmaker
import requests


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


def on_message(ws, message):
    from main import engine
    Session = sessionmaker(bind=engine)
    session = Session()

    json_obj = loads(message)
    # if json_obj["victim"]["corporation_id"] == 93593825:
    print("Kill recieved")
    message_queue.append(f"{json_obj['zkb']['url']}")
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
