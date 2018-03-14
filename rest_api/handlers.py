#!/usr/bin/env python
# -*- coding: utf-8 -*

import json
from datetime import datetime, timedelta
from tornado.web import RequestHandler

import config
from database.influxdb.influx import BaseInfluxdb


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
        self.render("templates/index.html")


class ShowIpFlowHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.render("templates/flow.html", title="流量监控系统")


class GetIpFlowHandler(BaseHandler):
    def get(self, *args, **kwargs):
        try:
            clock = (datetime.utcnow() - timedelta(seconds=60)).replace(minute=0, second=0, microsecond=0)
            influx_client = BaseInfluxdb(config.INFLUXDB_DB)
            ip = self.get_argument('ip', '')
            res = influx_client.get_ip_flow(ip, clock)
            self.write_response(res)
        except Exception as e:
            return e