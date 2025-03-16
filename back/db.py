import sqlite3
import base64
from config import *
import hashlib
import string

SPECIAL_CHARACTERS = string.punctuation
ENGLISH = string.ascii_letters
NUMBERS = string.digits

def hash_password(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8') + PASSWORD_SALT.encode('utf-8'))
    return sha256.hexdigest()

def start_db():
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    return con, cur

def delete_user(id):
    try:
        con, cur = start_db()
        cur.execute('DELETE FROM user WHERE id=?', (id,))
        con.commit()
        con.close()
        return True
    except:
        return "error"
    
def change_passwords(id, password):
    try:
        con, cur = start_db()
        cur.execute('UPDATE user SET password=? WHERE id=?', (password, id))
        con.commit()
        con.close()
        return True
    except:
        return "error"
    
def change_emails(id, email):
    try:
        con, cur = start_db()
        cur.execute('UPDATE user SET email=? WHERE id=?', (email, id))
        con.commit()
        con.close()
        return True
    except:
        return "error"
    
def change_nicknames(id, nickname):
    try:
        con, cur = start_db()
        cur.execute('UPDATE user SET nickname=? WHERE id=?', (nickname, id))
        con.commit()
        con.close()
        return True
    except:
        return "error"

def make_table():
    try:
        con, cur = start_db()
        cur.execute('CREATE TABLE IF NOT EXISTS user (id TEXT PRIMARY KEY, email TEXT default NULL, nickname TEXT, money integer, password TEXT, admin integer default 0)')
        cur.execute('CREATE TABLE IF NOT EXISTS stocks (id TEXT, stock_name TEXT, stock_count integer)')
        con.commit()
        con.close()
        return True
    except:
        return "error"
    
def add_user(id, nickname, password, admin=0, email=None, money=0):
    try:
        con, cur = start_db()
        cur.execute('INSERT INTO user (id, email, nickname, money, password, admin) VALUES (?, ?, ?, ?, ?, ?)', (id, email, nickname, money, password, admin))
        con.commit()
        con.close()
        return True
    except:
        return "error"

def check_id_string(id):
    # 아이디는 4자 이상 20자 이하의 영문자, 숫자, _ 만 가능
    if len(id) < 4 or len(id) > 20:
        return False
    for c in id:
        if not c.isalnum() and c != '_':
            return False
    return True

def check_password_string(password):
    # 비밀번호는 8자 이상 20자 이하의 영문자, 숫자, 특수문자만 가능
    if len(password) < 8 or len(password) > 20:
        return False
    for c in password:
        if c not in SPECIAL_CHARACTERS and c not in ENGLISH and c not in NUMBERS:
            return False
    return True

def check_password(id, password):
    try:
        con, cur = start_db()
        cur.execute('SELECT password FROM user WHERE id=?', (id,))
        user_password = cur.fetchone()[0]
        con.close()
        password = hash_password(password)
        if user_password == password:
            return True
        else:
            return False
    except:
        return "error"
    
def check_user(id):
    try:
        con, cur = start_db()
        cur.execute('SELECT * FROM user WHERE id=?', (id,))
        user = cur.fetchone()
        con.close()
        if user:
            return True
        else:
            return False
    except:
        return "error"
    
def add_money(id, money):
    try:
        chkuser = check_user(id)
        if chkuser == False:
            return "error"
        else:
            con, cur = start_db()
            cur.execute('SELECT money FROM user WHERE id=?', (id,))
            user_money = cur.fetchone()[0]
            user_money += money
            cur.execute('UPDATE user SET money=? WHERE id=?', (user_money, id))
            con.commit()
            return True
    except:
        return "error"

def add_stock(id, stock_name, stock_count):
    try:
        con, cur = start_db()
        cur.execute('SELECT * FROM stocks WHERE id=? AND stock_name=?', (id, stock_name))
        stock = cur.fetchone()
        if stock:
            stock_count += stock[2]
            cur.execute('UPDATE stocks SET stock_count=? WHERE id=? AND stock_name=?', (stock_count, id, stock_name))
        else:
            cur.execute('INSERT INTO stocks (id, stock_name, stock_count) VALUES (?, ?, ?)', (id, stock_name, stock_count))
        con.commit()
        con.close()
        return True
    except:
        return "error"
    
def check_stock(id, stock_name, stock_count):
    try:
        con, cur = start_db()
        cur.execute('SELECT * FROM stocks WHERE id=? AND stock_name=?', (id, stock_name))
        stock = cur.fetchone()
        if stock:
            if stock[2] < stock_count:
                return False
            else:
                return True
        else:
            return False
    except:
        return "error"
    
def check_money(id, money):
    try:
        con, cur = start_db()
        cur.execute('SELECT money FROM user WHERE id=?', (id,))
        user_money = cur.fetchone()[0]
        if user_money < money:
            return False
        else:
            return True
    except:
        return "error"
    
def check_stock_zero(id):
    try:
        con, cur = start_db()
        
        cur.execute('DELETE FROM stocks WHERE id=? AND stock_count<=0', (id,))
        con.commit()
        con.close()
        return True
    except:
        return "error"

def check_stock_user(id, stock_name):
    try:
        con, cur = start_db()
        cur.execute('SELECT * FROM stocks WHERE id=? AND stock_name=?', (id, stock_name))
        stock = cur.fetchone()
        if stock:
            return stock
        else:
            return False
    except:
        return "error"

def get_user(id):
    try:
        con, cur = start_db()
        cur.execute('SELECT * FROM user WHERE id=?', (id,))
        user = cur.fetchone()
        con.close()
        return user
    except:
        return "error"