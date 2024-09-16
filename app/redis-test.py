import time
import redis



redisCli = redis.Redis(
    host='localhost',
    port=6379,
    charset="utf-8",
    decode_responses=True,
    db=1
    )


"""
info keyspace
flushdb
config get databases


.get() #checks in O(1)
.exists() #O(n) time

"""


connection = redisCli.ping()
print(connection)

name = 'rohit'
surname = 'rank'
redisCli.set(name=name, value=surname, ex=10)
time.sleep(5)
print(redisCli.get('rohit'))
time.sleep(2)
print(redisCli.get('rohit'))
print(redisCli.exists('rohit'))
time.sleep(3)
print(redisCli.get('rohit'))
print(redisCli.exists('rohit'))

