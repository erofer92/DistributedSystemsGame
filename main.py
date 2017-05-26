
from server import Server
from database import DataBase

server_addr = ('192.168.0.29', 5555)

try:
    path = 'sqlite.db'
    db = DataBase(path)
    server = Server(server_addr, db)
    server.start_service()
except SystemExit:
    print('Exiting...')
