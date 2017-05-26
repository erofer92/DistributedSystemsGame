
import sqlite3
from user import User, Player


def select(func):
    def inner(self, *args):
        try:
            self.connection = sqlite3.connect(self.path)
            self.cursor = self.connection.cursor()
            obj = func(self, *args)
            self.connection.commit()
            self.connection.close()
            return obj
        except sqlite3.DatabaseError:
            print('SelectError', *args[1:])
            return None
    return inner


def insert(func):
    def inner(self, *args):
        try:
            with sqlite3.connect(self.path) as self.connection:
                self.cursor = self.connection.cursor()
                obj = func(self, *args)
                self.cursor.close()
                return obj
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

    def result(self, cl):
        value = self.cursor.fetchone()
        return cl(*value) if value is not None else None

    @select
    def select_user_by_login_pass(self, user):
        sql = ''' SELECT *
                  FROM user
                  WHERE user.login = ? AND user.password = ?
              '''
        tupl = (user.login, user.password)
        self.cursor.execute(sql, tupl)
        return self.result(User)

    @select
    def select_user_by_login(self, user):
        sql = ''' SELECT *
                  FROM user
                  WHERE user.login = ?
              '''
        tupl = (user.login, )
        self.cursor.execute(sql, tupl)
        return self.result(User)

    @insert
    def insert_user(self, user):
        sql = ''' INSERT INTO user
                  VALUES (?, ?, ?, ?, ?, ?)
              '''
        user.id = self.__next_id('user')
        tupl = (*user.tupl(), user.player.id)
        self.connection.execute(sql, tupl)
        return user

    @select
    def select_player(self, user):
        sql = ''' SELECT player.*
                  FROM user JOIN player ON user.player = player.id
                  WHERE user.id = ?
              '''
        tupl = (user.id, )
        self.cursor.execute(sql, tupl)
        player = self.result(Player)
        return player

    @insert
    def insert_player(self, player):
        sql = ''' INSERT INTO player
                  VALUES (?, ?, ?, ?, ?)
              '''
        player.id = self.__next_id('player')
        self.connection.execute(sql, player.tupl())
        return player
