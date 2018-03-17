#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
from database.redis.redis import BaseRedisDb

redis_client = BaseRedisDb()


class FlowEntry(object):
    def __init__(self, **kwargs):
        self.datapath = kwargs.get("datapath", None)

    @staticmethod
    def _add(datapath, priority, match, inst, hard_timeout, idle_timeout, cookie, table_id, flags, buffer_id=0):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath,
                                    command=ofproto.OFPFC_ADD,
                                    buffer_id=buffer_id,
                                    priority=priority,
                                    match=match,
                                    instructions=inst,
                                    hard_timeout=hard_timeout,
                                    idle_timeout=idle_timeout,
                                    cookie=cookie,
                                    table_id=table_id,
                                    flags=flags)
        else:
            mod = parser.OFPFlowMod(datapath=datapath,
                                    command=ofproto.OFPFC_ADD,
                                    priority=priority,
                                    match=match,
                                    instructions=inst,
                                    hard_timeout=hard_timeout,
                                    idle_timeout=idle_timeout,
                                    cookie=cookie,
                                    table_id=table_id,
                                    flags=flags)
        datapath.send_msg(mod)

    @staticmethod
    def _remove(datapath, priority, match, cookie, table_id, buffer_id=0):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_praser
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath,
                                    command=ofproto.OFPFC_DELETE,
                                    priority=priority,
                                    match=match,
                                    cookie=cookie,
                                    table_id=table_id,
                                    buffer_id=buffer_id)
        else:
            mod = parser.OFPFlowMod(datapath=datapath,
                                    command=ofproto.OFPFC_DELETE,
                                    priority=priority,
                                    match=match,
                                    cookie=cookie,
                                    table_id=table_id)
        datapath.send_msg(mod)

    def add(self, *args):
        raise NotImplementedError

    def remove(self, *args):
        raise NotImplementedError


class BaseFlowEntry(FlowEntry):
    def __init__(self, **kwargs):
        super(BaseFlowEntry, self).__init__(**kwargs)

    def add(self, datapath, priority, match, inst, hard_timeout, idle_timeout, cookie, table_id, flags):
        self._add(datapath=datapath, priority=priority, match=match, inst=inst, hard_timeout=hard_timeout,
                  idle_timeout=idle_timeout, cookie=cookie, table_id=table_id, flags=flags)

    def remove(self, datapath, priority, match, inst, cookie, table_id, buffer_id=0):
        self._remove(datapath=datapath, priority=priority, match=match, cookie=cookie, table_id=table_id)


class IpFlowEntry(FlowEntry):
    def __init__(self, **kwargs):
        super(IpFlowEntry, self).__init__(**kwargs)

    def add(self, datapath, ip, priority=3, cookie=101, table_id=0, hard_timeout=0, idle_timeout=config.FLOW_TIME_OUT):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        in_match = parser.OFPMatch(eth_type=0x800, ipv4_dst=ip)
        out_match = parser.OFPMatch(eth_type=0x800, ipv4_src=ip)

        normal_inst = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, normal_inst)]

        if not redis_client.has_key("temp_flow-3-%s" % ip):
            self._add(datapath=datapath, priority=priority, match=in_match, inst=inst, hard_timeout=hard_timeout,
                      idle_timeout=idle_timeout,cookie=cookie, table_id=table_id, flags=ofproto.OFPFF_SEND_FLOW_REM)
            print("IpFlow added: match: %s" % str(in_match))
            self._add(datapath=datapath, priority=priority, match=out_match, inst=inst, hard_timeout=hard_timeout,
                      idle_timeout=idle_timeout,cookie=cookie, table_id=table_id, flags=ofproto.OFPFF_SEND_FLOW_REM)
            print("IpFlow added: match: %s" % str(in_match))
            redis_key = "temp_flow-%s-%s" % (priority, ip)
            redis_client.set_key(redis_key, 0, timeout=config.FLOW_TIME_OUT)

    def remove(self, datapath, ip, priority=3, cookie=101, table_id=0):
        parser = datapath.ofproto_parser

        in_match = parser.OFPMatch(eth_type=0x800, ip_dst=ip)
        out_match = parser.OFPMatch(eth_type=0x800, ip_src=ip)

        self._remove(datapath=datapath, priority=priority, match=in_match, cookie=cookie, table_id=table_id)
        print("IpFlow removed: match: %s" % str(in_match))
        self._remove(datapath=datapath, priority=priority, match=out_match, cookie=cookie, table_id=table_id)
        print("IpFlow removed: match: %s" % str(in_match))
        redis_key = "temp_flow-%s-%s" % (priority, ip)
        redis_client.del_key(redis_key)