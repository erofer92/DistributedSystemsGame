
from server import Server
from database import DataBase

port = 5555
server_addr = ('192.168.0.17', port)

try:
    path = 'sqlite.db'
    db = DataBase(path)
    server = Server(server_addr, db)
    server.start_service()
except SystemExit:
    print('Exiting...')
