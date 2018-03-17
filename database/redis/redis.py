#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis

import config


class RedisListEmpty(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BaseRedisDb(object):
    def __init__(self, host=config.REDISHOST, port=config.REDISPORT, db=0):
        super(BaseRedisDb, self).__init__()
        self.client = redis.StrictRedis(host, port, db=db, decode_responses=True)

    def get_client(self):
        return self.client

    def push(self, k, v):
        self.client.rpush(k, v)

    def watch_list(self, k, timeout):
        try:
            _, inst = self.client.blpop(k, timeout)
        except TypeError as e:
            # raise RedisListEmpty(e)
            return None
        return inst

    def get_len(self, k):
        if self.client.type(k) == "list":
            return self.client.llen(k)
        else:
            return 0

    def pop(self, k):
        k_len = self.get_len(k)
        v_list = []
        if not k_len:
            return v_list
        else:
            for i in range(k_len):
                item = self.client.lpop(k)
                if item not in v_list:
                    v_list.append(item)
            return v_list

    def add_hash(self, name, timeout=None, **kwargs):
        for k, v in kwargs.items():
            self.client.hset(name, k, v)
        if timeout:
            self.client.expire(name, timeout)

    def del_hash(self, name):
        self.client.delete(name)

    def modify_hash(self, name, k, v):
        self.client.hset(name, k, v)

    def hash_del(self, name, k):
        self.client.hdel(name, k)

    def get_hash_key(self, name, k):
        return self.client.hget(name, k)

    def get_hash_keys(self, name):
        return self.client.hgetall(name)

    def get_keys(self, pattern='*'):
        return self.client.keys(pattern=pattern)

    def set_key(self, k, v, timeout=None):
        self.client.set(k, v)
        if timeout:
            self.client.expire(k, timeout)

    def get_key(self, k):
        return self.client.get(k)

    def del_key(self, k):
        self.client.delete(k)

    def has_key(self, k):
        return self.client.exists(k)

    def get_ttl(self, k):
        return self.client.ttl(k)