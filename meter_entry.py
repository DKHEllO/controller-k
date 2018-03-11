#!/usr/bin/env python
# -*- coding: utf-8 -*-


class MeterEntry(object):
    def __init__(self):
        pass

    @staticmethod
    def _add(datapath, meter_id, rate, burst_size):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        _rate = int(rate) * 1024
        if burst_size:
            _burst_size = int(burst_size) * 1024
        else:
            _burst_size = int(rate) * 1024 / 2
        bands = [parser.OFPMeterBandDrop(rate=_rate, burst_size=_burst_size)]
        mod = parser.OFPMeterMod(datapath=datapath,
                                 command=ofproto.OFPMC_ADD,
                                 flags=ofproto.OFPMF_KBPS | ofproto.OFPMF_BURST,
                                 meter_id=meter_id,
                                 bands=bands)
        datapath.send_msg(mod)

    @staticmethod
    def _remove(datapath, meter_id):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        mod = parser.OFPMeterMod(datapath=datapath,
                                 command=ofproto.OFPMC_DELETE,
                                 meter_id=meter_id)
        datapath.send_msg(mod)

    def add(self, *args):
        raise NotImplementedError

    def remove(self, *args):
        raise NotImplementedError


class BaseMeterEntry(MeterEntry):
    def __init__(self):
        super(BaseMeterEntry, self).__init__()

    def add(self, datapath, meter_id, rate, burst_size):
        self._add(datapath=datapath, meter_id=meter_id, rate=rate, burst_size=burst_size)

    def remove(self, datapath, meter_id):
        self._remove(datapath=datapath, meter_id=meter_id)