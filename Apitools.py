import requests

corpid = 98239554
url = "https://esi.evetech.net/latest/"
character_id = 93593825
response = requests.get(
    f"{url}characters/{character_id}/?datasource=tranquility")
print(response.content)
