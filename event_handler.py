#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ryu.lib.packet import packet
from ryu.lib.packet import ethernet, ipv4

from flow_entry import BaseFlowEntry, IpFlowEntry


def packet_in_handler(msg):
    datapath = msg.datapath
    ip_flow_entry = IpFlowEntry()

    pkt = packet.Packet(msg.data)
    eth = pkt.get_protocols(ethernet.ethernet)[0]
    ip = pkt.get_protocol(ipv4.ipv4)

    if ip:
        dst = ip.dst
        ip_flow_entry.add(datapath, dst)


def flow_stats_reply_handler(msg, flow_stats, counter):
    datapath = msg.datapath
    ofp_parser = datapath.ofproto_parser

    if not counter.get('flow'):
        counter['flow'] = 0

    for stats in msg.body:
        counter['flow'] += 1
        match = stats.match
        priority = stats.priority
        ip_dst = match.get('ipv4_dst')

        flow_id = ip_dst

        if not flow_stats.get(flow_id):
            ip_info = {
                'byte': 0,
                'packet': 0,
            }
            flow_stats.update(ip_info)
            byte_count = 0
            packet_count = 0
        else:
            tmp_byte_count = stats.byte_count - flow_stats[flow_id]['byte']
            if tmp_byte_count < 0:
                # 流表被重新添加
                byte_count = stats.byte_count
                packet_count = stats.packet_count
            else:
                byte_count = tmp_byte_count
                packet_count = stats.packet_count - flow_stats[flow_id]['packet']
        flow_stats[flow_id] = stats.byte_count
        flow_stats[flow_id] = stats.packet_count


def err_msg_handler(msg):
    type_dic = {
        0: 'Hello protocol failed',
        1: 'Request was not understood',
        2: 'Error in action description',
        3: 'Error in instruction list',
        4: 'Error in match',
        5: 'Problem modifying flow entry',
        6: 'Problem modifying group entry',
        7: 'OFPT_PORT_MOD failed',
        8: 'Table mod request failed',
        9: 'Queue operation failed',
        10: 'Switch config request failed',
        11: 'Controller Role request failed',
        12: 'Error in meter',
        13: 'Setting table features failed',
        0xffff: 'Experimenter error messages'
    }
    code_dic = {
        0: {
            0: 'No compatible version',
            1: 'Permissions error'
        },
        1: {
            0: 'ofp_header.version not supported',
            1: 'ofp_header.type not supported',
            2: 'ofp_multipart_request.type not supported',
            3: 'Experimenter id not supported(in ofp_experimenter_header or ofp_multipart_request or ofp_multipart_reply)',
            4: 'Experimenter type not supported',
            5: 'Permissions error',
            6: 'Wrong request length for type',
            7: 'Specified buffer has already been used',
            8: 'Specified buffer does not exist',
            9: 'Specified table-id invalid or does not exist',
            10: 'Denied because controller is slave',
            11: 'Invalid port',
            12: 'Invalid packet in packet-out',
            13: 'ofp_multipart_request overflowed the assigned buffer'
        },
        2: {
            0: "Unknown action type",
            1: "Length problem in actions",
            2: "Unknown experimenter id specified",
            3: "Unknown action type for experimenter id",
            4: "Problem validating output action",
            5: "Bad action argument",
            6: "Permissions error",
            7: "Can't handle this many actions",
            8: "Problem validating output queue",
            9: "Invalid group id in forward action",
            10: "Action can't apply for this match, or Set-Field missing prerequisite",
            11: "Action order is unsupported for the action list in an Apply-Actions instruction",
            12: "Actions uses an unsupported tag/encap",
            13: "Unsupported type in SET_FIELD action",
            14: "Length problem in SET_FIELD action",
            15: "Bad arguement in SET_FIELD action",
        },
        3: {
            0: "Unknown instruction",
            1: "Switch or table does not support the instruction",
            2: "Invalid Table-Id specified",
            3: "Metadata value unsupported by datapath",
            4: "Metadata mask value unsupported by datapath",
            5: "Unknown experimenter id specified",
            6: "Unknown instruction for experimenter id",
            7: "Length problem in instrucitons",
            8: "Permissions error",
        },
        4: {
            0: "Unsupported match type apecified by the match",
            1: "Length problem in math",
            2: "Match uses an unsupported tag/encap",
            3: "Unsupported datalink addr mask - switch does not support arbitrary datalink address mask",
            4: "Unsupported network addr mask - switch does not support arbitrary network addres mask",
            5: "Unsupported combination of fields masked or omitted in the match",
            6: "Unsupported field type in the match",
            7: "Unsupported value in a match field",
            8: "Unsupported mask specified in the match",
            9: "A prerequisite was not met",
            10: "A field type was duplicated",
            11: "Permissions error",
        },
        5: {
            0: "Unspecified error",
            1: "Flow not added because table was full",
            2: "Table does not exist",
            3: "Attempted to add overlapping flow with CHECK_OVERLAP flag set",
            4: "Permissions error",
            5: "Flow not added because of unsupported idle/hard timeout",
            6: "Unsupported or unknown command",
            7: "Unsupported or unknown flags",
        },
        6: {
            0: "",
            1: "",
            2: "Switch does not support unequal load sharing with select groups",
            3: "The group table is full",
            4: "The maximum number of action buckets for a group has been exceeded",
            5: "Switch does not support groups that forward to groups",
            6: "This group cannot watch the watch_port or watch_group specified",
            7: "Group entry would cause a loop",
            8: "Group not modified because a group MODIFY attempted to modify a non-existent group",
            9: "Group not deleted because another group is forwarding to it",
            10: "Unsupported or unknown group type",
            11: "Unsupported or unknown command",
            12: "Error in bucket",
            13: "Error in watch port/group",
            14: "Permissions error",
        },
        7: {
            0: "Specified port does not exist",
            1: "Specified hardware address does not match the port number",
            2: "Specified config is invalid",
            3: "Specified advertise is invalid",
            4: "Permissions error",
        },
        8: {
            0: "Specified table does not exist",
            1: "Specified config is invalid",
            2: "Permissions error",
        },
        9: {
            0: "Invalid port (or port does not exist)",
            1: "Queue does not exist",
            2: "Permissions error",
        },
        10: {
            0: "Specified flags is invalid",
            1: "Specified len is invalid",
            2: "Permissions error (depracated) New or updated Ryu applications shall use OFPSCFC_EPERM The variable name is a typo of in specifications before v1.31 (EXT-208)",
        },
        11: {
            0: "Stale Message: old generation_id",
            1: "Controller role change unsupported",
            2: "Invalid role",
        },
        12: {
            0: "Unspecified error",
            1: "Meter not added because a Meter ADD attempted to replace an existing Meter",
            2: "Meter not added because Meter specified is invalid",
            3: "Meter not modified because a Meter MODIFY attempted to modify a non-existent Meter",
            4: "Unsupported or unknown command",
            5: "Flag configuration unsupported",
            6: "Rate unsupported",
            7: "Burst size unsupported",
            8: "Band unsupported",
            9: "Band value unsupported",
            10: "No more meters availabile",
            11: "The maximum number of properties for a meter has been exceeded",
        },
        13: {
            0: "Specified table does not exist",
            1: "Invalid metadata mask",
            2: "Unknown property type",
            3: "Length problem in properties",
            4: "Unsupported property value",
            5: "Permissions error",
        }
    }
    err_type = int(msg.type)
    err_code = int(msg.code)
    print(type_dic[err_type], code_dic[err_type][err_code])


def flow_removed_handler(msg):
    datapath = msg.datapath
    ofp = datapath.ofproto

    if msg.reason == ofp.OFPRR_IDLE_TIMEOUT:
        reason = 'IDLE TIMEOUT'
    elif msg.reason == ofp.OFPRR_HARD_TIMEOUT:
        reason = 'HARD TIMEOUT'
    elif msg.reason == ofp.OFPRR_DELETE:
        reason = 'DELETE'
    elif msg.reason == ofp.OFPRR_GROUP_DELETE:
        reason = 'GROUP DELETE'
    else:
        reason = 'unknown'
    print(reason, "table_id: {table_id} priority: {priority} cookie: {cookie} match: {match}".format(
        table_id=msg.table_id, priority=msg.priority, cookie=msg.cookie,
        match=str(msg.match)))
