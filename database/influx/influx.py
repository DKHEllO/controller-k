#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
from influxdb import InfluxDBClient


class BaseInfluxdb(InfluxDBClient):
    def __init__(self, db_name=None, username=None, password=None):
        super(BaseInfluxdb, self).__init__()
        self.client = InfluxDBClient(host=config.INFLUXDBHOST, port=config.INFLUXDBPORT, timeout=config.INFLUXDBTIMEOUT,
                                     username=username if username else config.INFLUXDBUSER,
                                     password=password if password else config.INFLUXDBPASS, database=db_name,
                                     ssl=config.INFLUXDB_SSL)
        self.db_name = db_name

