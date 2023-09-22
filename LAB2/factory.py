from typing import List
from player import Player
import player_pb2 as PlayersList
import xml.etree.ElementTree as ET


class PlayerFactory:
    def to_json(self, players: List[Player]):
        return list(map(lambda player: {
            "nickname": player.nickname,
            "email": player.email,
            "date_of_birth": player.date_of_birth.strftime("%Y-%m-%d"),
            "xp": player.xp,
            "class": player.cls
        }, players))

    def from_json(self, list_of_dict: List):
        return [
            Player(
                dict["nickname"],
                dict["email"],
                dict["date_of_birth"],
                dict["xp"],
                dict["class"])
            for dict in list_of_dict
        ]

    def from_xml(self, xml_string: str):
        xml = ET.ElementTree(ET.fromstring(xml_string))
        players_nodes = xml.getroot().iter("player")
        arr = []
        for player_node in players_nodes:
            nickname = player_node.find("nickname").text
            email = player_node.find("email").text
            date_of_birth = player_node.find("date_of_birth").text
            xp = int(player_node.find("xp").text)
            cls = player_node.find("class").text
            arr.append(
                Player(
                    nickname=nickname,
                    email=email,
                    date_of_birth=date_of_birth,
                    xp=xp,
                    cls=cls
                )
            )

        return arr

    def to_xml(self, list_of_players: List[Player]):
        root = ET.Element("data")
        for player in list_of_players:
            player_node = ET.SubElement(root, "player")

            nickname = ET.SubElement(player_node, "nickname")
            nickname.text = player.nickname

            email = ET.SubElement(player_node, "email")
            email.text = player.email

            date_of_birth = ET.SubElement(player_node, "date_of_birth")
            date_of_birth.text = player.date_of_birth.strftime("%Y-%m-%d")

            xp = ET.SubElement(player_node, "xp")
            xp.text = str(player.xp)

            cls = ET.SubElement(player_node, "class")
            cls.text = player.cls

        return ET.tostring(root)

    def from_protobuf(self, binary):
        player_list = PlayersList.PlayersList()
        player_list.ParseFromString(binary)
        return [
            Player(
                player.nickname,
                player.email,
                player.date_of_birth,
                player.xp,
                PlayersList.Class.Name(player.cls)
            )
            for player in player_list.player
        ]

    def to_protobuf(self, list_of_players):
        player_list = PlayersList.PlayersList()
        for player in list_of_players:
            player_list.player.add(
                nickname=player.nickname,
                email=player.email,
                date_of_birth=player.date_of_birth.strftime("%Y-%m-%d"),
                xp=player.xp,
                cls=PlayersList.Class.Value(player.cls)
            )

        return player_list.SerializeToString()
