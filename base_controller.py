#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, HANDSHAKE_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib import hub

import event_handler
from flow_entry import BaseFlowEntry


class Controller(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.write_time = 0
        self.flow_stats = {}
        self.counter = {'flow': 0}
        self.datapath_dic = {}
        self.monitor_thread = hub.spawn(self.monitor)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        print('switch in')
        datapath = ev.msg.datapath
        dpid = datapath.id
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        base_flow_entry = BaseFlowEntry()

        self.datapath_dic.update({dpid: datapath})

        to_normal = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]

        match_port_3 = parser.OFPMatch(eth_type=0x800, in_port=3)
        inst_normal = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, to_normal)]

        match = parser.OFPMatch()
        to_controller = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
        inst_nom_cotr = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, to_normal),
                parser.OFPInstructionActions(ofproto.OFPIT_WRITE_ACTIONS, to_controller)]

        base_flow_entry.add(datapath=datapath, priority=1, match=match, inst=inst_nom_cotr, hard_timeout=0, idle_timeout=0,
                            table_id=0, flags=ofproto.OFPFF_NO_PKT_COUNTS | ofproto.OFPFF_NO_BYT_COUNTS, cookie=100)
        base_flow_entry.add(datapath=datapath, priority=1, match=match_port_3, inst=inst_normal, hard_timeout=0,
                            idle_timeout=0,table_id=0, flags=ofproto.OFPFF_NO_PKT_COUNTS | ofproto.OFPFF_NO_BYT_COUNTS,
                            cookie=100)

    def monitor(self):
        while True:
            for dpid, datapath in self.datapath_dic.items():
                self._request_flow_stats(datapath)
            hub.sleep(1)

    def _request_flow_stats(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath, 0, ofproto.OFPTT_ALL, ofproto.OFPP_ANY, ofproto.OFPG_ANY, 0, 0)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        print('packet in')
        msg = ev.msg
        event_handler.packet_in_handler(msg)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        msg = ev.msg
        event_handler.flow_stats_reply_handler(msg=msg, flow_stats=self.flow_stats, counter=self.counter)

    @set_ev_cls(ofp_event.EventOFPErrorMsg, [HANDSHAKE_DISPATCHER, MAIN_DISPATCHER, CONFIG_DISPATCHER])
    def _error_msg_handler(self, ev):
        msg = ev.msg
        event_handler.err_msg_handler(msg)

    @set_ev_cls(ofp_event.EventOFPFlowRemoved, MAIN_DISPATCHER)
    def _flow_removed_handler(self, ev):
        msg = ev.msg
        event_handler.flow_removed_handler(msg)
