from struct import pack, unpack_from
from Tribler.dispersy.conversion import BinaryConversion


class StatisticsConversion(BinaryConversion):

    MTU_SIZE = 1500

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

    # TODO fix for dictionaries larger than MTU (split message)
    def _encode_statistics_response(self, message):
        stats_type = message.payload.stats_type
        records = message.payload.records
        # pattern_len = self.PUBKEY_LENGTH + 4
        # pattern_occ = min(self.MTU_SIZE / pattern_len, len(records) / columns)
        # pattern = "!i%s" % (("%isi" % self.PUBKEY_LENGTH) * pattern_occ)
        # return pack(pattern, int(stats_type), *records),
        packed = pack("!i", stats_type)
        # r = public key of other peers
        for r in records:
            # print "packing r: %d, %s %d" % (len(r), r, records[r])
            # packed = packed + pack("!H%dsi" % len(r), len(r), r, records[r])
            peer_id = r[0]
            value = r[1]
            packed = packed + pack("!H%dsi" % len(peer_id), len(peer_id), peer_id, value)

        # iterate through records
        # for i in range(0, len(records) / columns):
        #    r = records[i * columns]
        #    value = records[i * columns + 1]
        #    packed = packed + pack("!Hsi", len(r), r, value)
        return packed,

    def _decode_statistics_response(self, placeholder, offset, data):
        stats_type, = unpack_from("!i", data, offset)
        offset += 4
        records = []
        while offset < len(data):
            len_key, = unpack_from("!H", data, offset)
            if len_key < 1:
                break
            offset += 2
            # key = data[offset: offset + len_key]
            key, = unpack_from("!%ds" % len_key, data, offset)
            offset += len_key
            value = data[offset: offset + 4]
            offset += 4
            r = [key, value]
            # r = unpack_from(("!%dsi" % keylength), data, offset)
            # offset += keylength + 4
            records.append(r)
        return offset, placeholder.meta.payload.implement(stats_type, records)

        # records = []
        # while offset < len(data):
        #    r = unpack_from("!%isi" % self.PUBKEY_LENGTH, data, offset)
        #    records.append(r)
        #    offset += self.PUBKEY_LENGTH + 4

        # return offset, placeholder.meta.payload.implement(stats_type, records)
