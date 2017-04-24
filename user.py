
import json


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
    def __init__(self, *args, **kwargs):
        self.id = args[0] if args else 0
        self.name = args[1] if args else kwargs['Name']
        self.email = args[2] if args else kwargs['Email']
        self.login = args[3] if args else kwargs['Login']
        self.password = args[4] if args else kwargs['Password']
        self.player = None  # type: Player

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
        return json.dumps({
            'Id': self.id,
            'Name': self.name,
            'Email': self.email,
            'Login': self.login,
            'Password': self.password,
            })


class Player(object):
    """ Quando recebida via JSON, tem código 2 """
    def __init__(self, *args, **kwargs):
        self.id = args[0] if args else kwargs['Id']
        self.login = args[1] if args else kwargs['Login']
        self.x = args[2] if args else kwargs['X']
        self.y = args[3] if args else kwargs['Y']
        self.d = args[4] if args else kwargs['D']
        self.coins = args[5] if args else kwargs['Coins']

    def dic(self):
        return {
            'Id': self.id,
            'Login': self.login,
            'X': self.x,
            'Y': self.y,
            'D': self.d,
            'Coins': self.coins
            }

    def tupl(self):
        return self.id, self.login, self.x, self.y, self.d, self.coins

    def json(self):
        return json.dumps(self.dic())


class PlayerList(object):
    """ Esse objeto só é utilizado quando um usuário faz login no jogo
        para atualizar toda sua lista de jogadores na tela.
        Quando enviada via JSON, tem código 3
    """

    def __init__(self, player_list: list):
        self.player_list = player_list

    def dic(self):
        return [player.dic() for player in self.player_list]

    def json(self):
        return json.dumps(self.dic())
