import json


class JsonUtils:
    _instance = None
    watched_systems: dict = {}
    valid_systems: dict = {}
    server_configs: dict = {}

    def __init__(self) -> None:
        raise RuntimeError("Call instance() for singleton pattern")

    '''Singleton Pattern!'''
    @classmethod
    def instance(self):
        if self._instance is None:
            self._instance = self.__new__(self)

        return self._instance


    def add_system(self, system: str):
        if system.lower() not in self.watched_systems.keys():
            self.watched_systems[system.lower()] = 1
            self.update_system_json()
            return True
        return False

    def remove_system(self, system: str):
        if system.lower() in self.watched_systems.keys():
            del self.watched_systems[system.lower()]
            self.update_system_json()
            return True
        return False


    def str_to_json(self, string: str):
        return json.loads(string)

JSONUTILS = JsonUtils.instance()
