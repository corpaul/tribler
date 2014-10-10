from Tribler.dispersy.payload import Payload


class StatisticsRequestPayload(Payload):
    '''
    Request statistics for key 'key' from peer.
    '''

    class Implementation(Payload.Implementation):

        def __init__(self,
                     key):
            assert isinstance(key, unicode)
            self.key = key


class StatisticsResponsePayload(Payload):

    class Implementation(Payload.Implementation):

        def __init__(self, meta, key, statistic):
            super(StatisticsResponsePayload.Implementation, self).__init__(meta)
            self.key = key
            self.statistic = statistic
