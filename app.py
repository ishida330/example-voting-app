from flask import Flask, render_template, request, make_response, g
from redis import StrictRedis
import os
import socket
import random
import json

option_a = os.getenv('OPTION_A', "Cats")
option_b = os.getenv('OPTION_B', "Dogs")
redis_password = os.getenv('REDIS_PASSWORD', "Dogs")
hostname = socket.gethostname()

app = Flask(__name__)

def cleardb():
    redis = StrictRedis(host='redis', port=6379, db=0, password='redis_password', charset="utf-8", decode_responses=True)
    redis.flushdb()

@app.route("/clear", methods=['POST','GET'])
def clear():
    cleardb()
    resp = make_response(render_template(
        'index.html',
        option_a=option_a,
        option_b=option_b,
        hostname=hostname,
        CatCount=0,
        DogCount=0,
        vote="a"
    ))
    return resp

def get_redis():
    if not hasattr(g, 'redis'):
        # g.redis = Redis(host="127.0.0.1", db=0, socket_timeout=5)
        g.redis = StrictRedis(host='redis', port=6379, db=0, password='redis_password', charset="utf-8", decode_responses=True)
    return g.redis

@app.route("/", methods=['POST','GET'])
def hello():
    CatCount = 0
    DogCount = 0


    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:-1]

    vote = None
    if request.method == 'POST':
        # add a vote
        redis = get_redis()
        vote = request.form['vote']
        data = json.dumps({'voter_id': voter_id, 'vote': vote})
        redis.rpush('votes', data)
        # count votes
        votes = redis.lrange('votes', 0, -1)
        for v in votes:
            v = json.loads(v)
            if v['vote'] == 'a':
                CatCount += 1
            else:
                DogCount += 1
    # render html
    resp = make_response(render_template(
        'index.html',
        option_a=option_a,
        option_b=option_b,
        hostname=hostname,
        CatCount=CatCount,
        DogCount=DogCount,
        vote=vote,
    ))
    resp.set_cookie('voter_id', voter_id)
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
