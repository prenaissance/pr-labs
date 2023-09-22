from datetime import datetime


class Player:
    def __init__(self, nickname: str, email: str, date_of_birth: str, xp: str, cls: str):
        self.nickname = nickname
        self.email = email
        self.date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d")
        self.xp = xp
        self.cls = cls

    def __repr__(self):
        return f"<Player[nickname = {self.nickname}]>"