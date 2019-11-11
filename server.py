import json
import redis
import pymongo
#from storage.py import Storage
from flask import Flask
from flask import request

class Storage:

    def __init__(self, redis_client, table):
        self.redis_client = redis_client
        self.mongo_table = table

    def put(self, key, value):
        self.mongo_table.insert_one({'key':key, 'value' :value})

    def get(self, key):
        if not self.redis_client.exists(key):
            value = self.mongo_table.find_one({'key': key})
            if value is not None:
                self.redis_client.set(key, str(value))
                return value['value']
            else:
                return None
        return self.redis_client.get(key)

    def delete(self, key):
        self.redis_client.delete(key)
        self.mongo_table.delete_many({'key': key})


app = Flask(__name__)

redisClient = redis.Redis(host='rediska', port=6379, decode_responses=True)
mongoClient = pymongo.MongoClient(host='mongo', port=27017)
storage = Storage(redisClient, mongoClient['hw8']['cache'])


@app.route('/cache/<key>', methods=['GET'])
def get_value(key):
    value = storage.get(key)
    if value is None:
        return '', 404
    return json.loads(value)


@app.route('/cache/<key>', methods=['DELETE'])
def delete_value(key):
    storage.delete(key)
    return '', 204


@app.route('/cache/<key>', methods=['PUT'])
def add_value(key):
    if not request.is_json:
        return '', 400
    content = request.get_json()
    value = json.dumps(content)
    storage.put(key, value)
    return '', 201


if __name__ == '__main__':
    app.run()