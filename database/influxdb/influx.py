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

    def get_ip_flow(self, ip, clock):
        query_str = "SELECT * FROM ip_flow_10s WHERE time>='%s' AND ip='%s'" % (clock, ip)
        res = self.client.query(query_str)
        for records in res:
            return records


if __name__ == '__main__':
    influx_client = BaseInfluxdb(config.INFLUXDB_DB).client
    res = influx_client.query("select * from ip_flow_10s where ip='10.0.0.2'")
    print(res)
