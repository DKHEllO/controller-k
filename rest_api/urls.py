#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rest_api.handlers import IndexHandler, GetIpFlowHandler, ShowIpFlowHandler

url = [
    (r"/", IndexHandler),
    (r"/get_flow", GetIpFlowHandler),
    (r"/show_flow", ShowIpFlowHandler)
]