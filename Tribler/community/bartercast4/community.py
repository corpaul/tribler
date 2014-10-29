# Written by Cor-Paul Bezemer
from conversion import StatisticsConversion
from payload import StatisticsRequestPayload, StatisticsResponsePayload

from Tribler.dispersy.authentication import MemberAuthentication
from Tribler.dispersy.community import Community
from Tribler.dispersy.conversion import DefaultConversion
from Tribler.dispersy.destination import CandidateDestination
from Tribler.dispersy.distribution import DirectDistribution
from Tribler.dispersy.message import Message, DelayMessageByProof
from Tribler.dispersy.resolution import PublicResolution
import logging


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

BartercastStatisticTypes = enum(TORRENTS_RECEIVED=1)


def getBartercastStatisticDescription(t):
    if t is BartercastStatisticTypes.TORRENTS_RECEIVED:
        return "torrents_received"
    return "unknown"


class BarterCommunity(Community):
    def __init__(self, dispersy, master, my_member):
        super(BarterCommunity, self).__init__(dispersy, master, my_member)
        self._dispersy = dispersy
        self._logger = logging.getLogger(self.__class__.__name__)

    def initiate_meta_messages(self):
        return super(BarterCommunity, self).initiate_meta_messages() + [
            Message(self, u"stats-request",
                    MemberAuthentication(),
                    PublicResolution(),
                    DirectDistribution(),
                    CandidateDestination(),
                    StatisticsRequestPayload(),
                    self.check_stats_request,
                    self.on_stats_request),
            Message(self, u"stats-response",
                    MemberAuthentication(),
                    PublicResolution(),
                    DirectDistribution(),
                    CandidateDestination(),
                    StatisticsResponsePayload(),
                    self.check_stats_response,
                    self.on_stats_response)
        ]
        

    def initiate_conversions(self):
        return [DefaultConversion(self), StatisticsConversion(self)]

    @property
    def dispersy_sync_response_limit(self):
        return 1

    @property
    def dispersy_sync_skip_enable(self):
        return False

    @property
    def dispersy_sync_cache_enable(self):
        return False

    def create_stats_request(self, candidate, stats_type):
        self._logger.info("Creating stats-request for type %d" % stats_type)
        meta = self.get_meta_message(u"stats-request")
        message = meta.impl(authentication=(self._my_member,),
                            distribution=(self.claim_global_time(),),
                            destination=(candidate,),
                            payload=(stats_type,))
        self._dispersy._forward([message])
        #self._dispersy.store_update_forward([message], store, update, forward)

    def check_stats_request(self, messages):
        self._logger.info("OUT: stats-request")
        for message in messages:
            allowed, _ = self._timeline.check(message)
            if allowed:
                yield message
            else:
                yield DelayMessageByProof(message)

    def on_stats_request(self, messages):
        self._logger.info("IN: stats-request")
        for message in messages:
            self._logger.info("stats-request: %s %s" % (message._distribution.global_time, message.payload.stats_type))
            # send back stats-response
            self.create_stats_response(message.payload.stats_type, message.candidate)

    # todo
    def create_stats_response(self, stats_type, candidate):
        self._logger.info("OUT: stats-response")
        meta = self.get_meta_message(u"stats-response")
        self._logger.info("sending stats: %s" % self._dispersy._statistics.bartercast)
        #records = self._dispersy._statistics.bartercast
        records = ["peerid1", 123, "peerid2", 456]

        message = meta.impl(authentication=(self._my_member,),
                            distribution=(self.claim_global_time(),),
                            destination=(candidate,),
                            payload=(stats_type, records))
        self._dispersy._forward([message])
        #self._dispersy.store_update_forward([message], store, update, forward)

    def check_stats_response(self, messages):
        for message in messages:
            allowed, _ = self._timeline.check(message)
            if allowed:
                yield message
            else:
                yield DelayMessageByProof(message)

    def on_stats_response(self, messages):
        self._logger.info("IN: stats-response")
        for message in messages:
            self._logger.info("stats-response: %s %s %s"
                               % (message._distribution.global_time, message.payload.stats_type, message.payload.records))
