from struct import pack, unpack_from

from Tribler.dispersy.member import Member
from Tribler.dispersy.conversion import BinaryConversion
from Tribler.dispersy.message import DropPacket
from Tribler.Core.Utilities.encoding import encode, decode


class StatisticsConversion(BinaryConversion):

    def __init__(self, community):
        super(StatisticsConversion, self).__init__(community, "\x02")
        self.define_meta_message(chr(1), community.get_meta_message(u"stats-request"),
                                 self._encode_statistics_request, self._decode_statistics_request)
        #self.define_meta_message(chr(2), community.get_meta_message(u"stats-response"),
        #                         self._encode_statistics_response, self._decode_statistics_response)

    def _encode_statistics_request(self, message):
        text = message.payload.key.encode("UTF-8")
        return pack("!B", len(text)), text

    def _decode_statistics_request(self, placeholder, offset, data):
        if len(data) < offset + 1:
            raise DropPacket("Insufficient packet size")

        text_length, = unpack_from("!B", data, offset)
        offset += 1

        try:
            text = data[offset:offset + text_length].decode("UTF-8")
            offset += text_length
        except UnicodeError:
            raise DropPacket("Unable to decode UTF-8")

        return offset, placeholder.meta.payload.implement(text)

    #def _encode_statistics_response(self, message):
    #    text = message.payload.key.encode("UTF-8")
    #    statistic = message.payload.statistic.encode("UTF-8")
    #    return pack("!B", len(text)), text