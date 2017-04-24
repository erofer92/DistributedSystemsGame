
import sqlite3
from user import User, Player


def select(func):
    def inner(self, *args):
        try:
            self.connection = sqlite3.connect(self.path)
            self.cursor = self.connection.cursor()
            # print('SELECT   :', func.__name__)
            r = func(self, *args)
            self.connection.commit()
            self.connection.close()
            return r
        except sqlite3.DatabaseError:
            print('SelectError', *args[1:])
            return None
    return inner


def insert(func):
    def inner(self, *args):
        try:
            with sqlite3.connect(self.path) as self.connection:
                self.cursor = self.connection.cursor()
                # print('INSERT   :', func.__name__)
                r = func(self, *args)
                self.cursor.close()
                return r
        except sqlite3.IntegrityError:
            print('InsertError -', str(args[1:]), 'já está no banco!')
    return inner


class DataBase(object):

    def __init__(self, path: str):
        self.path = path
        self.connection = None  # type: sqlite3.Connection
        self.cursor = None  # type: sqlite3.Cursor

    def __next_id(self, table):
        sql = 'SELECT max(id) FROM ' + table
        self.cursor.execute(sql)
        value = self.cursor.fetchone()[0]
        return value + 1 if value is not None else 1

    def result(self, _class):
        value = self.cursor.fetchone()
        return _class(*value) if value is not None else None

    @select
    def select_user_by_login_pass(self, user: User) -> User:
        sql = ''' SELECT *
                  FROM user
                  WHERE user.login = ? AND user.password = ?
              '''
        tupl = (user.login, user.password)
        self.cursor.execute(sql, tupl)
        return self.result(User)

    @select
    def select_user_by_login(self, user: User) -> User:
        sql = ''' SELECT *
                  FROM user
                  WHERE user.login = ?
              '''
        tupl = (user.login, )
        self.cursor.execute(sql, tupl)
        return self.result(User)

    @insert
    def insert_user(self, user: User) -> User:
        sql = ''' INSERT INTO user
                  VALUES (?, ?, ?, ?, ?, ?)
              '''
        tupl = (self.__next_id('user'), *user.tupl()[1:], user.player.id)
        self.connection.execute(sql, tupl)
        sql = ''' SELECT *
                  FROM user
                  WHERE user.login = ?
              '''
        tupl = (user.login, )
        self.cursor.execute(sql, tupl)
        return self.result(User)

    @select
    def select_player(self, user: User) -> Player:
        sql = ''' SELECT player.*
                  FROM user JOIN player ON user.player = player.id
                  WHERE user.id = ?
              '''
        tupl = (user.id, )
        self.cursor.execute(sql, tupl)
        r = self.result(Player)
        return r

    @insert
    def insert_player(self, player: Player) -> Player:
        sql = ''' INSERT INTO player
                  VALUES (?, ?, ?, ?, ?, ?)
              '''
        tupl = (self.__next_id('player'), *player.tupl()[1:])
        self.connection.execute(sql, tupl)
        sql = ''' SELECT *
                  FROM player
                  WHERE player.login = ?
              '''
        tupl = (player.login, )
        self.cursor.execute(sql, tupl)
        return self.result(Player)
