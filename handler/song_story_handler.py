from handler.base_handler import BaseHandler
from Tools.log import logging
from model.model import Story, User

#返回歌曲的故事信息
class SongStoryHandler(BaseHandler):
    def get(self, song_id):
        #if(not self.valid_user()):
        rep = {"code": 0, "errinfo": "success"}

        try:
            rows = self.db.query(Story).filter(Story.song_id==song_id).all()
        except Exception as e:
            rep["code"] = 1
            rep["errinfo"] = "数据查询失败"
            logging.error(e)
            self.write(rep)
            return


        try:
            result = []
            for row in rows:
                user_row = self.db.query(User).filter(User.user_id==row.user_id).first()

                tmp_dic = {}
                tmp_dic["longitude"] = row.longitude
                tmp_dic["latitude"] = row.latitude
                tmp_dic["story_id"] = row.story_id
                tmp_dic["content"] = row.content
                tmp_dic["user_id"] = row.user_id
                tmp_dic["user_name"] = user_row.user_name
                result.append(tmp_dic)

            rep["data"] = result
            rep["code"] = 0
            rep["errinfo"] = "success"
        except Exception as e:
            rep["code"] = 2
            rep["errinfo"] = "数据库没有对应的字段"
            logging.error(e)
            self.write(rep)
            return

        self.write(rep)

