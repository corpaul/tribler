from struct import pack, unpack_from

from Tribler.dispersy.member import Member
from Tribler.dispersy.conversion import BinaryConversion
from Tribler.dispersy.message import DropPacket
from Tribler.Core.Utilities.encoding import encode, decode


class StatisticsConversion(BinaryConversion):

    def __init__(self, community):
        super(StatisticsConversion, self).__init__(community, "\x02")
        self.define_meta_message(chr(1), community.get_meta_message(u"stats-request"), self._encode_statistics_request, self._decode_statistics_request)
        self.define_meta_message(chr(2), community.get_meta_message(u"stats-response"), self._encode_statistics_response, self._decode_statistics_response)

    def _encode_statistics_request(self, message):
        payload = message.payload
        return encode((payload.key))

    def _decode_statistics_request(self, placeholder, offset, data):
        try:
            offset, values = decode(data, offset)
            if len(values) != 1:
                raise ValueError
        except ValueError:
            raise DropPacket("Unable to decode the stats-request")
