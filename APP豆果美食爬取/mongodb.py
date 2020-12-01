import pymongo



class Connect_mongo(object):
    def __init__(self):
        self.client = pymongo.MongoClient()

    def insert_data(self,item):
        self.client.douguomeishi.foodinfo.insert(item)


mongo_info = Connect_mongo()

