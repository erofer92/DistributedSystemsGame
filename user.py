
import json

from enum import Enum

class User(object):
    """ Formato da mensagem JSON:
        {'Id': self.id, 'Name': self.name, 'Email': self.email,
        'Login': self.login, 'Password': self.password}

        Quando recebida via JSON, tem código 0.
        Quando for enviado ao cliente, o 'id' será igual a x,
        onde x é um valor diferente de 0 e com valor igual ao registro do banco.
        Caso x seja igual a 0, não foi possível criar um registro,
        pois já existe um registro com o login especificado.
    """
    def __init__(self, Id=0, Name='', Email='', Login='', Password='', Player=None, **kwargs):
        self.id = Id
        self.name = Name
        self.email = Email
        self.login = Login
        self.password = Password
        self.player = Player  # type: Player

    def tupl(self):
        return self.id, self.name, self.email, self.login, self.password

    def dic(self):
        return {
            'Id': self.id,
            'Name': self.name,
            'Email': self.email,
            'Login': self.login,
            'Password': self.password
            }

    def json(self):
        return json.dumps(self.dic())


class Player(object):
    """ Quando recebida via JSON, tem código 2 """
    def __init__(self, Id=0, Login='', X=100, Y=100, D=3, IsLeader=False, **kwargs):
        self.id = Id
        self.login = Login
        self.x = X
        self.y = Y
        self.d = D
        self.leader = IsLeader

    def dic(self):
        return {
            'Id': self.id,
            'Login': self.login,
            'X': self.x,
            'Y': self.y,
            'D': self.d,
            'IsLeader': self.leader
            }

    def tupl(self):
        return self.id, self.login, self.x, self.y, self.d

    def json(self):
        return json.dumps(self.dic())


class PlayerList(object):
    """ Esse objeto só é utilizado quando um usuário faz login no jogo
        para atualizar toda sua lista de jogadores na tela.
        Quando enviada via JSON, tem código 3
    """

    def __init__(self, player_list):
        self.player_list = player_list

    def dic(self):
        return [player.dic() for player in self.player_list]

    def json(self):
        return json.dumps(self.dic())

class PlayerDirection(Enum):

    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3
