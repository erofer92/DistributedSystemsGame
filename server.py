
import socket
import threading
import json
from datetime import datetime
from message import Message
from database import DataBase
from user import Player, PlayerList, PlayerDirection
from timer import Timer

BUFFER = 2048


class ClientHandler(object):

    def __init__(self, client: socket.socket, server, database: DataBase):
        self.server = server
        self.server_db = database
        self.client = client
        self.client_addr = client.getpeername()
        self.logged = False
        self.player = None
        self.user = None
        self.last_message_time = datetime.now()

    def handle(self):
        """ Responsável por cuidar da conexão e das mensagens de um cliente """
        try:
            while True:
                message = self.client.recv(BUFFER)
                message = message.decode('utf8')
                if not message:
                    break
                self.execute_action(message)
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
            print('[-] Falha ao decodificar o JSON. Descartando.', request)
            return

        print("RECEIVING :    ", message.json())

        if message.cod == 0:
            self.registry_handler(message)

        elif message.cod == 1:
            self.login_handler(message)

        elif message.cod == 2:
            self.player_handler(message)

        elif message.cod == 3:
            pass

        elif message.cod == 4:
            if message.object.login == self.player.login:
                self.logout_handler(message)
            else:
                self.server.disconnect_enemy(self, message)

        print("SENDING   :    ", message.json())

    def registry_handler(self, message: Message):
        user = self.server_db.select_user_by_login(message.object)
        if not user:
            self.player = Player(Login=message.object.login)
            message.object.player = self.player = self.server_db.insert_player(self.player)
            user = self.server_db.insert_user(message.object)
        else:
            user.id = 0

        message.object = user

        self.client.send(message.json().encode())

    def login_handler(self, message: Message):
        user = self.server_db.select_user_by_login_pass(message.object)

        if self.logged:
            self.refuse_connection(Message)

        if user:
            self.player = self.server_db.select_player(user)
            self.logged = True
            if not self.server.in_game_handler_list:
                self.player.leader = True
            self.server.in_game_handler_list.insert(0, self)
            message.object = PlayerList(self.server.player_list())
            message.cod = 3
        self.client.send(message.json().encode())

        if not user:
            return

        self.client.recv(BUFFER)

        if len(self.server.in_game_handler_list) == 1:
            self.server.timer.start()

        msg = str(self.server.timer.remaining)
        self.client.send(msg.encode())

    def player_handler(self, message: Message):

        if not self.logged:
            pass  # evitar tentativas de alterar a movimentação do player sem que esteja logado

        if self.logged:
            message.cod = 2
            self.player.x = message.object.x
            self.player.y = message.object.y
            self.player.d = message.object.d
            self.player.leader = message.object.leader
            self.server.broadcast(self, message.json().encode())
            self.last_message_time = datetime.now()

    def logout_handler(self, message: Message):

        if self.logged:
            self.server.broadcast(self, message.json().encode())
            logoutlogin = message.object.login
            if self.player.leader:
                handler = self.server.in_game_handler_list[len(self.server.in_game_handler_list) - 2]
                handler.update_position()
                message.cod = 2
                message.object = handler.player
                message.object.leader = True
                self.server.broadcast(self, message.json().encode())
                print('[+] O Lider foi alterado:', message.object.login)

            if self.player.login == logoutlogin:
                self.finish()

            if not self.server.in_game_handler_list:
                self.server.timer = Timer()

    def finish(self):
        if self in self.server.handler_list:
            if self in self.server.in_game_handler_list:
                self.server.in_game_handler_list.remove(self)
            self.server.handler_list.remove(self)

        self.client.close()
        print('[+] Client ' + self.client_addr[0] + ':' + str(self.client_addr[1]) + ' disconnected')

    def refuse_connection(self, message: Message):
        pass

    def increment_position(self, increase):
        if self.player.d == PlayerDirection.LEFT.value:
            self.player.x -= int(increase)

        elif self.player.d == PlayerDirection.UP.value:
            self.player.y -= int(increase)

        elif self.player.d == PlayerDirection.RIGHT.value:
            self.player.x += int(increase)

        elif self.player.d == PlayerDirection.DOWN.value:
            self.player.y += int(increase)

    def update_position(self):
        """
        Calcula a quantidade de pixels que o player andou desde
        a ultima mensagem recebida e prevê a posição atual do player.
        """
        speed = 235 # definido pelo cliente
        # time = 0.1  # definido pelo cliente
        now = datetime.now()
        delay = now - self.last_message_time
        delay = (delay.seconds + delay.microseconds / 1000000) / 2  # em segundos
        self.last_message_time = now  # atualiza a hora que sua posição foi atualizada.
        increase = delay * speed
        self.increment_position(increase)


class Server(object):

    def __init__(self, address: tuple, database: DataBase):
        self.server_db = database
        self.address = address
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.handler_list = []
        self.in_game_handler_list = []
        self.timer = Timer()

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

    def disconnect_enemy(self, handler, message: Message):

        for handl in self.in_game_handler_list:
            if handl.player.login != handler.player.login:
                handl.client.send(message.json().encode())

    def broadcast(self, handler, message: str):
        '''
        map(lambda h: h.client.send(message) if h.client.getpeername() != handler.client.getpeername() else None,
            self.in_game_handler_list)
        '''
        for handl in self.in_game_handler_list:
            try:
                if handl.client.getpeername() != handler.client.getpeername():
                    handl.client.send(message)
            except OSError:
                pass  # Essa exceção pode ocorrer quando um cliente foi
                # desconectado porem ainda não saiu da lista

    def player_list(self):
        # return [h.player for h in self.in_game_handler_list]
        l = []
        for h in self.in_game_handler_list:
            h.update_position()
            l.append(h.player)
        return l

    def update_leader(self):
        self.in_game_handler_list[len(self.in_game_handler_list) -1].player.leader = True
