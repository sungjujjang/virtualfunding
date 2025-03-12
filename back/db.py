import sqlite3

def start_db():
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    return con, cur

def make_table():
    con, cur = start_db()
    cur.execute('CREATE TABLE IF NOT EXISTS user (id TEXT PRIMARY KEY, email TEXT default NULL, nickname TEXT, money integer, password TEXT, admin integer default 0)')
    cur.execute('CREATE TABLE IF NOT EXISTS stocks (id TEXT, stock_name TEXT, stock_count integer)')
    con.commit()
    con.close()
    
def add_user(id, nickname, money, password, admin, email=None):
    con, cur = start_db()
    cur.execute('INSERT INTO user (id, email, nickname, money, password, admin) VALUES (?, ?, ?, ?, ?, ?)', (id, email, nickname, money, password, admin))
    con.commit()
    con.close()

def add_stock(id, stock_name, stock_count):
    con, cur = start_db()
    cur.execute('INSERT INTO stocks (id, stock_name, stock_count) VALUES (?, ?, ?)', (id, stock_name, stock_count))
    con.commit()
    con.close()