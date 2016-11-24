import falcon
import json
from bson.json_util import dumps
from pymongo import MongoClient

MONGO_URI = 'mongodb://localhost:27017/'
MONGO_DATABASE = 'adiaoc'
MONGO_COLLECTION = 'adiaoc_crawl_item'

client = MongoClient(MONGO_URI)
db = client[MONGO_DATABASE]
collection = db[MONGO_COLLECTION]

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

class APIResource:
	def on_get(self, req, resp):
		limit = req.get_param_as_int('limit') or 10
		result = collection.find()[:limit]
		resp.body = dumps(result)
		
		for item in result:
			collection.update({'_id': item['_id']}, {"$set": { "seen": True }}, upsert=False)
		
class Main:
	def on_get(self, req, res):
		res.body = 'We dont talk any more ....'

api = falcon.API()
api.add_route('/api/v1', APIResource())
api.add_route('/', Main())