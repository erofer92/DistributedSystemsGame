
import json
from user import User, Player, PlayerList


class Message(object):
    """
        Formato da mensagem JSON:
        {'cod': str, 'object': object}

        cod pode ter os valores:
        cod = '00' - object = User
        cod = '01' - object = Login
        cod = '02' - object = Logout
        cod = '03' - object = Player
        cod = '04' - object = PlayerList

        Cliente - Servidor
        cod = '00' - requisição de novo registro
                     formato da mensagem: {'cod': 00, 'object': User}
        cod = '01' - requisição de login
                     formato da mensagem: {'cod': 01, 'object': Login}
        cod = '02' - requisição de logout (não recebe resposta, apenas fecha a conexão)
                     formato da mensagem: {'cod': 02, 'object': Logout}
        cod = '03' - envio de coordenadas
                     formato da mensagem: {'cod': 03, 'object': Player}
        cod = '04' - não se aplica
        Servidor - Cliente
        cod = '00' - retorna o registro com o id preenchido.
                     id do objeto registro igual a 0 significa registro negado.
                     caso o id do registro seja maior que 0 o registro ocorreu
                     com sucesso e o usuário pode se logar.
                     mensagem de retorno:
                     sucesso: {'cod': 00, 'object': registry} com registry.id > 0
                     erro: {'cod': 00, 'object': registry} com registry.id = 0
        cod = '01' - retorna um Player caso o login seja efetuado com sucesso.
                     caso o login ou senha estejam inválidos, retorna o objeto
                     login de volta.
                     mensagem de retorno:
                     sucesso: {'cod': 03, 'object': player}
                     erro: {'cod': 01, 'object': login}
        cod = '02' - não envia nada ao cliente. Apenas remove-o da lista de Players
                     e finaliza a conexão.
                     mensagem de retorno:
                     sucesso: não tem
                     erro: não tem
        cod = '03' - envia um Player com suas coordenadas atualizadas, para que o
                     cliente atualize os movimentos dos outros jogadores em sua tela.
                     mensagem de retorno:
                     sucesso: {'cod': 03, 'object': player}
                     erro: não tem
        cod = '04' - envia uma lista de Players. Essa lista é enviada apenas quando o
                     cliente loga, para que todos os Players apareçam em sua tela sem
                     que necessite uma mensagem para cada player.
                     sucesso: {'cod': 04, 'object': PlayerList}
                     erro: não tem
    """
    def __init__(self, Cod=0, Object=None):
        self.cod = Cod
        self.object = self.__convert_object(Object)

    def __convert_object(self, d):
        if self.cod == 0:
            return User(**d)  # Tentativa de Registro
        elif self.cod == 1:
            return User(**d)  # Tentativa de Login
        elif self.cod == 2:
            return Player(**d)  # Coordenadas / Movimentação
        elif self.cod == 3:
            return PlayerList(**d)  # Apenas Servidor - Cliente
        elif self.cod == 4:
            return Player(**d)  # Logout

    def dic(self):
        return {
            'Cod': self.cod,
            'Object': self.object.dic()
        }

    def json(self):
        return json.dumps(self.dic())
