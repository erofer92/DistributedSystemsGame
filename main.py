
from server import Server
from database import DataBase

server_addr = ('192.168.0.29', 5555)

try:
    db = DataBase('sqlite.db')
    server = Server(server_addr, db)
    server.start_service()
except SystemExit:
    print('Exiting...')
