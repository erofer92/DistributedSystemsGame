
import socket
import threading
import json
from message import Message
from database import DataBase
from user import Player, PlayerList

BUFFER = 2048


class ClientHandler(object):

    def __init__(self, client: socket.socket, server, database: DataBase):
        self.server = server
        self.server_db = database
        self.client = client
        self.client_addr = client.getpeername()
        self.is_logged = False
        self.player = None
        self.user = None

    def handle(self):
        """ Responsável por cuidar da conexão e das mensagens de um cliente """
        try:
            while True:
                message = self.client.recv(BUFFER)
                message = message.decode('utf8')
                if not message:
                    break
                print('RECEIVING:', message)
                self.execute_action(message)
                print('SENDING  :', message)
        except ConnectionResetError:
            pass
        except OSError:
            pass
        self.finish()

    def execute_action(self, request: str):
        try:
            message = Message(**json.loads(request))
        except KeyError:
            print('[-] Existem chaves incorretas na mensagem: ' + request)
            return
        except json.JSONDecodeError:
            print('[-] Falha ao decodificar o JSON: ' + request)
            return

        if message.cod == 0:
            self.registry_handler(message)

        elif message.cod == 1:
            self.login_handler(message)

        elif message.cod == 2:
            self.player_handler(message)

        elif message.cod == 3:
            pass

        elif message.cod == 4:
            self.logout_handler(message)

    def registry_handler(self, message: Message):
        user = self.server_db.select_user_by_login(message.object)
        if not user:
            # posição x,y=50,50 (centro da tela) e d=3 (direita).
            self.player = Player(0, message.object.login, 50, 50, 3, 0)
            self.player = self.server_db.insert_player(self.player)
            message.object.player = self.player
            user = self.server_db.insert_user(message.object)
        else:
            user.id = 0
        message.object = user

        self.client.send(message.json().encode())

    def login_handler(self, message: Message):
        user = self.server_db.select_user_by_login_pass(message.object)
        if user:
            self.player = self.server_db.select_player(user)
            self.is_logged = True
            self.server.in_game_handler_list.insert(0, self)
            message.object = PlayerList(self.server.player_list())
            message.cod = 3
        # print(message.json())
        self.client.send(message.json().encode())

    def player_handler(self, message: Message):
        if self.is_logged:
            message.cod = 2
            self.player.x = message.object.x
            self.player.y = message.object.y
            self.player.d = message.object.d
            self.player.coins = message.object.coins
            message.object = self.player
            self.server.broadcast(self, message.json().encode())

    def logout_handler(self, message: Message):
        if self.is_logged:
            self.server.broadcast(self, message.json().encode())
            self.finish()

    def finish(self):
        if self in self.server.in_game_handler_list:
            self.server.in_game_handler_list.remove(self)

        if self in self.server.handler_list:
            self.server.handler_list.remove(self)

        self.client.close()
        print('[+] Client ' + self.client_addr[0] + ':' + str(self.client_addr[1]) + ' disconnected')


class Server(object):

    def __init__(self, address: tuple, database: DataBase):
        self.server_db = database
        self.address = address
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.handler_list = []
        self.black_list = [str]  # ip
        self.in_game_handler_list = []  # ClientHandler

    def start_service(self):
        """
        Inicializa o socket principal para escutar novas conexões.
        Ao receber uma nova conexão, inicializa uma thread para tratá-la.
        """
        self.socket.bind(self.address)
        self.socket.listen(5)
        print('[+] Server listening on ' + self.address[0] + ':' + str(self.address[1]))
        try:
            while True:
                c_socket, c_address = self.socket.accept()
                if c_address[0] in self.black_list:
                    # NOT IMPLEMENTED
                    print('[-] Connection refused:', c_address[0], ':', c_address[1],
                          '\n[-] The IP address is in the Black List')
                    c_socket.close()
                    continue
                self.new_handler(c_socket, c_address)
        except KeyboardInterrupt:
            print()
            self.shutdown()

    def new_handler(self, c_socket: socket, c_addr: tuple):
        handler = ClientHandler(c_socket, self, self.server_db)
        self.handler_list.append(handler)
        client_thread = threading.Thread(target=ClientHandler.handle, args=(handler,))
        client_thread.daemon = True
        client_thread.start()
        print('[+] New connection: ', c_addr[0], ':', c_addr[1])

    def shutdown(self):
        self.close_all_connections()
        self.socket.close()
        print('[+] Server is OFF')

    def close_all_connections(self):
        print('[+] Closing connections')
        while self.handler_list:
            self.handler_list[0].finish()
        print('[+] All connections were closed')

    def broadcast(self, handler: ClientHandler, message):
        for handl in self.in_game_handler_list:
            try:
                if handl.client.getpeername() != handler.client.getpeername():
                    handl.client.send(message)
            except OSError:
                pass  # Essa exceção pode ocorrer quando um cliente foi
                # desconectado porem ainda não saiu da lista

    def remove_from_client_list(self, handler: ClientHandler):
        if handler in self.in_game_handler_list:
            self.in_game_handler_list.remove(handler)
            print('[+] Cliente ' + str(handler.client.getpeername()) +
                  'removido da lista de clientes que estão jogando!')
        if handler in self.handler_list:
            self.handler_list.remove(handler)
            print('[+] Cliente ' + str(handler.client.getpeername()) +
                  'removido da lista de clientes conectados!')

    def player_list(self):
        return [handler.player for handler in self.in_game_handler_list]
