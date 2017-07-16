import json
from handler.base_handler import BaseHandler
from datetime import datetime 
import logging
import urllib.request
from Tools.log import logging
from model.model import Story, LikeStory

class StoryHandler(BaseHandler):
    def post(self):
        "留下故事信息"
        body = json.loads(self.request.body)

        content = body["content"]
        song_id = body["song_id"]
        longitude = body["longitude"]
        latitude = body["latitude"]
        user_id = body["user_id"]

        story = Story(
            content=content,
            song_id=song_id,
            up=0,
            longitude=longitude,
            latitude=latitude,
            created_at=datetime.utcnow(),
            user_id=user_id
        )

        try:
            self.db.add(story)
            self.db.commit()
        except Exception as e:
            logging.error(e)
            self.db.rollback()
            err = {'code': 1, 'errinfo': '存入故事失败'}
            self.write(err)
            return

        sql = '''
            SELECT story_id FROM story WHERE song_id = {0} AND user_id = {1}
        '''.format(song_id, user_id)
        try:
            results = self.db.execute(sql).fetchone()
        except Exception as e:
            logging.error(e)
            self.db.rollback()
            err = {'code': 2, 'errinfo': '获取故事id失败'}
            self.write(err)
            return
        print(results)
        story_id = results[0]
        url = "http://118.89.60.80:8000/story/feature"
        headers = {'Content-Type': 'application/json'}
        reqbody = {"story_id": story_id, "content": content}
        reqbody_json = json.dumps(reqbody).encode('utf-8')
        req = urllib.request.Request(url=url, headers=headers, data=reqbody_json)
        res = urllib.request.urlopen(req)
        res = json.loads(res.read().decode('utf-8'))
        print(res)
        info = {'code': 0, 'errinfo': 'OK'}
        self.write(info)

class PraiseHandler(BaseHandler):
    def post(self, story_id):
        "给故事点赞"
        postdata = self.request.body.decode('utf-8')
        if not postdata:
            err = {'code': 3, 'errinfo': 'post数据为空'}
            self.write(err)
            return
        postdata = json.loads(postdata)

        sql = '''
            SELECT * FROM likestory WHERE user_id = "{0}" AND story_id = {1}
        '''.format(postdata['user_id'], story_id)
        try:
            self.db.query(LikeStory).filter(LikeStory.user_id==postdata['user_id']).all()
            results = self.db.execute(sql).fetchall()
        except Exception as e:
            err = {'code': 1, 'errinfo': '查询用户是否喜欢过该首歌曲时失败'}
            self.write(err)
            logging.error(e)
            return
  
        if len(results) != 0:
            err = {'code': 2, 'errinfo': '已经点过赞了'}
            self.write(err)
            return

        sql = '''
            INSERT INTO likestory(user_id, story_id) VALUES("{0}", {1})
        '''.format(postdata['user_id'], story_id)
        try:
            self.db.execute(sql)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            err = {'code': 3, 'errinfo': '"用户喜欢故事"信息存入失败'}
            self.write(err)
            logging.error(e)
            return

        sql = '''
            UPDATE story SET up = up + 1 WHERE story_id = {0}
        '''.format(story_id)
        try:
            self.db.execute(sql)
            self.db.commit()
            info = {'code': 0, 'errinfo': 'OK'}
            self.write(info)
        except Exception as e:
            self.db.rollback()
            err = {'code': 4, 'errinfo': '更新点赞数失败'}
            self.write(err)
            logging.error(err)
            return
