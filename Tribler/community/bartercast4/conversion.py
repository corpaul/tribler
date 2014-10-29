from struct import pack, unpack, unpack_from

from Tribler.dispersy.member import Member
from Tribler.dispersy.conversion import BinaryConversion
from Tribler.dispersy.message import DropPacket
from Tribler.Core.Utilities.encoding import encode, decode

import json

class StatisticsConversion(BinaryConversion):

    def __init__(self, community):
        super(StatisticsConversion, self).__init__(community, "\x02")
        self.define_meta_message(chr(1), community.get_meta_message(u"stats-request"),
                                 self._encode_statistics_request, self._decode_statistics_request)
        self.define_meta_message(chr(2), community.get_meta_message(u"stats-response"),
                                 self._encode_statistics_response, self._decode_statistics_response)

    def _encode_statistics_request(self, message):
        stats_type = message.payload.stats_type
        return pack("!i", stats_type),

    def _decode_statistics_request(self, placeholder, offset, data):
        # if len(data) < offset + 1:
        #    raise DropPacket("Insufficient packet size")

        # text_length, = unpack_from("!i", data, offset)
        # offset += 1

        # try:
        #    text = data[offset:offset + text_length].decode("UTF-8")
        #    offset += text_length
        # except UnicodeError:
        #    raise DropPacket("Unable to decode UTF-8")
        stats_type, = unpack_from("!i", data, offset)
        offset += 4
        return offset, placeholder.meta.payload.implement(stats_type)

    def _encode_statistics_response(self, message):
        stats_type = message.payload.stats_type
        records = message.payload.records
        pattern_len = 20 + 4
        columns = 2
        # pattern_occ = 1500 / pattern_len
        pattern_occ = min(1500 / pattern_len, len(records) / columns)
        pattern = "!i%s" % ("20si" * pattern_occ)
        return pack(pattern, int(stats_type), *records),

    def _decode_statistics_response(self, placeholder, offset, data):
        stats_type, = unpack_from("!i", data, offset)
        offset += 4

        records = []
        while offset < len(data):
            r = unpack_from("!20si", data, offset)
            records.append(r)
            offset += 20 + 4

        return offset, placeholder.meta.payload.implement(stats_type, records)
