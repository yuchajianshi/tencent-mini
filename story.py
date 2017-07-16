import json
import pymysql
import time
with open('story.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

db = pymysql.connect("595f58f641420.gz.cdb.myqcloud.com", "cdb_outerroot", "mini123456", "tingwen", 5880, use_unicode=True, charset="utf8")
cursor = db.cursor()
cursor.execute("SET NAMES utf8")
cursor.execute("SET CHARACTER SET utf8")
cursor.execute("SET character_set_connection=utf8")
for songinfo in data:
    sql = '''
        INSERT INTO story(content, song_id, up, longitude, latitude, created_at, user_id)
        VALUES("{0}", {1}, {2}, "{3}", "{4}", {5}, {6})
	    '''.format(songinfo['content'], songinfo['song_id'], songinfo['up'], songinfo['longitude'], songinfo['latitude'], time.time(), songinfo['user_id'])
    try:
        cursor.execute(sql)
        db.commit()
    except :
        db.rollback()
        print("insert database error")
#print(sql)
db.close()
