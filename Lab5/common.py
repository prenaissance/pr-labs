from dataclasses import dataclass
import json


@dataclass
class Message:
    type: str
    payload: dict

    def to_json(self):
        return json.dumps(self.__dict__)

    def __str__(self):
        return self.to_json()

    @staticmethod
    def from_json(json_str: str) -> 'Message':
        dict = json.loads(json_str)
        return Message(dict["type"], dict["payload"])
