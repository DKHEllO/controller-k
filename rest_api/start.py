#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import tornado.concurrent
import tornado.gen
import tornado.httpserver
import tornado.ioloop
import tornado.web

import config
from rest_api.urls import url


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
}


def make_app():
    return tornado.web.Application(url, **settings)


def run():
    application = make_app()
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(config.RESTAPIPORT)
    tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    run()