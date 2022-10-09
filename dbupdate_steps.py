import json
from commands import *
import requests
from schema import *
from concurrent.futures import ThreadPoolExecutor


create_database()

url = "https://esi.evetech.net/latest"


"""

!!!!!!!!!!!!!!!  READ THIS   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    These functions are used to pull data from ESI, and populate the persistent json files, 
    which are used to re-build the database should it need to be deleted for a schema change.
    Absolutely never run these unless you know what you are doing!

"""


"""Populate Systems Database from ESI"""


def step1():
    session = Session()

    def submit_request(system):
        new_data = requests.get(
            f"{url}/universe/systems/{system}/?datasource=tranquility").json()
        entry = Systems(id=new_data['system_id'], name=new_data["name"],
                        constellation_id=new_data["constellation_id"])
        print(entry)
        session.add(entry)
        Session.remove()

    response = requests.get(f"{url}/universe/systems/?datasource=tranquility")
    data = response.json()

    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(submit_request, data)
    session.commit()
    Session.remove()
    print("Populate Systems dbupdate step finished")


"""Populate Constellations Database from ESI"""


def step2():
    session = Session()

    def submit_request(constellation):
        new_data = requests.get(
            f"{url}/universe/constellations/{constellation}/?datasource=tranquility").json()
        entry = Constellations(id=new_data['constellation_id'], name=new_data["name"],
                               region_id=new_data["region_id"])
        print(entry)
        session.add(entry)

    response = requests.get(
        f"{url}/universe/constellations/?datasource=tranquility")
    data = response.json()

    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(submit_request, data)
    session.commit()
    print("Populate Constellations dbupdate step finished")
    Session.remove()


"""Populate Regions Database from ESI"""


def step3():
    session = Session()

    def submit_request(region):
        new_data = requests.get(
            f"{url}/universe/regions/{region}/?datasource=tranquility").json()
        entry = Regions(id=new_data['region_id'], name=new_data["name"],)
        print(entry)
        session.add(entry)

    response = requests.get(
        f"{url}/universe/regions/?datasource=tranquility")
    data = response.json()

    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(submit_request, data)
    session.commit()
    print("Populate Regions dbupdate step finished")
    Session.remove()


def write_regions_to_json_file():
    session = Session()
    mydict = {}
    results = session.query(Regions).all()
    for region in results:
        mydict[region.name] = [
            region.id]
    obj = json.dumps(mydict, indent=4)
    with open("json/regions.json", "w") as file:
        file.write(obj)
    Session.remove()


def write_constellations_to_json_file():
    session = Session()
    mydict = {}
    results = session.query(Constellations).all()
    for constellation in results:
        mydict[constellation.name] = [
            constellation.id, constellation.region_id]
    obj = json.dumps(mydict, indent=4)
    with open("json/constellations.json", "w") as file:
        file.write(obj)
    Session.remove()


def write_systems_to_json_file():
    session = Session()
    mydict = {}
    results = session.query(Systems).all()
    for system in results:
        mydict[system.name] = [system.id, system.constellation_id]
    obj = json.dumps(mydict, indent=4)
    with open("json/systems.json", "w") as file:
        file.write(obj)
    Session.remove()


def write_corporations_to_json_file():
    session = Session()
    mydict = {}
    results = session.query(Corporations).all()
    for corp in results:
        mydict[corp.name] = [
            corp.id, corp.alliance_id]
    obj = json.dumps(mydict, indent=4)
    with open("json/corporations.json", "w") as file:
        file.write(obj)
    Session.remove()


def write_alliances_to_json_file():
    session = Session()
    mydict = {}
    results = session.query(Alliances).all()
    for ally in results:
        mydict[ally.name] = [
            ally.id]
    obj = json.dumps(mydict, indent=4)
    with open("json/alliances.json", "w") as file:
        file.write(obj)
    Session.remove()


def write_system_configurations_to_json_file():
    session = Session()
    mydict = {}
    results = session.query(ServerConfigs).all()
    for server in results:
        mydict[server.name] = [
            server.id, server.channel, server.muted]
    obj = json.dumps(mydict, indent=4)
    with open("json/server_configs.json", "w") as file:
        file.write(obj)
    Session.remove()


"""Run before database is deleted for schema reformatting!"""


def PREPARE_FOR_DB_DELETE():
    write_regions_to_json_file()
    write_systems_to_json_file()
    write_constellations_to_json_file()
    write_alliances_to_json_file()
    write_corporations_to_json_file()
    write_system_configurations_to_json_file()

