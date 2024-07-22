import sqlite3
# Создание базы данных
conn = sqlite3.connect('hh_ru.db')

cur = conn.cursor()

# cur.execute("PRAGMA foreign_keys = ON")
#
cur.execute('create table IF NOT EXISTS search(world_id INTEGER PRIMARY KEY, vacancy TEXT, city TEXT, count INTEGER, [from] INTEGER, [to] INTEGER)')
cur.execute('create table IF NOT EXISTS skills(id INTEGER PRIMARY KEY, name TEXT)')
cur.execute('''create table  IF NOT EXISTS requirements (
     world_id INTEGER,
     id_skill INTEGER)''')

conn.commit()
cur.close()
