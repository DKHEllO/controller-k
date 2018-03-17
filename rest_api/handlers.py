#!/usr/bin/env python
# -*- coding: utf-8 -*

import json
from datetime import datetime, timedelta
from tornado.web import RequestHandler

import config
from database.influxdb.influx import BaseInfluxdb
from database.redis.redis import BaseRedisDb

redis_client = BaseRedisDb()


class BaseHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)

    def write_response(self, response, _status=1, _err=''):
        self.set_header('Content-type', 'application/json')
        _response = {
            "success": _status,
            "data": response,
            "err_msg": _err
        }
        self.write(json.dumps(_response))
        self.finish()

    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.render('404.html')
        elif status_code == 500:
            self.render('500.html')
        else:
            self.write('error:' + str(status_code))


class IndexHandler(BaseHandler):
    def get(self, *args, **kwargs):
        ip_lsit = []
        keys = redis_client.get_keys("temp_flow-3-*")
        for key in keys:
            ip = key.split("-")[2]
            ip_lsit.append(ip)
        self.render("templates/index.html", items=ip_lsit)


class ShowIpFlowHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.render("templates/flow.html", title="流量监控系统")


class GetIpFlowHandler(BaseHandler):
    def get(self, *args, **kwargs):
        try:
            clock = (datetime.utcnow() - timedelta(seconds=60)).replace(microsecond=0)
            print(datetime.utcnow(), clock)
            influx_client = BaseInfluxdb(config.INFLUXDB_DB)
            ip = self.get_argument('ip', '')
            redis_keys = redis_client.get_keys("*\-*\-%s" % ip)
            if redis_keys:
                res = influx_client.get_ip_flow(ip, clock)
                self.write_response(res)
            else:
                self.write_response("", _status=0, _err="无该ip")
        except Exception as e:
            return e