# Written by Cor-Paul Bezemer
from conversion import StatisticsConversion
from payload import StatisticsRequestPayload, StatisticsResponsePayload

from Tribler.dispersy.authentication import MemberAuthentication
from Tribler.dispersy.community import Community
from Tribler.dispersy.conversion import DefaultConversion
from Tribler.dispersy.destination import CommunityDestination
from Tribler.dispersy.distribution import FullSyncDistribution
from Tribler.dispersy.message import Message, DelayMessageByProof
from Tribler.dispersy.resolution import PublicResolution
import logging
import json

class BarterCommunity(Community):
    def __init__(self, dispersy, master, my_member):
        super(BarterCommunity, self).__init__(dispersy, master, my_member)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._dispersy = dispersy

    def initiate_meta_messages(self):
        return super(BarterCommunity, self).initiate_meta_messages() + [
            Message(self, u"stats-request",
                    MemberAuthentication(),
                    PublicResolution(),
                    FullSyncDistribution(enable_sequence_number=False, synchronization_direction=u"DESC", priority=128),
                    CommunityDestination(node_count=10),
                    StatisticsRequestPayload(),
                    self.check_stats_request,
                    self.on_stats_request),
            Message(self, u"stats-response",
                    MemberAuthentication(),
                    PublicResolution(),
                    FullSyncDistribution(enable_sequence_number=False, synchronization_direction=u"DESC", priority=128),
                    CommunityDestination(node_count=10),
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

    def create_stats_request(self, candidate, key):
        meta = self.get_meta_message(u"stats-request")
        message = meta.impl(authentication=(self._my_member,),
                            distribution=(self.claim_global_time(),),
                            payload=(key,))
        self._dispersy._endpoint.send([candidate], [message])
        # self.send_packet([candidate], u"stats-request", message)

    def check_stats_request(self, messages):
        for message in messages:
            allowed, _ = self._timeline.check(message)
            if allowed:
                yield message
            else:
                yield DelayMessageByProof(message)

    def on_stats_request(self, messages):
        for message in messages:
            self._logger.error("stats-request: %s %s" % (message._distribution.global_time, message.payload.key))
            # send back stats-response
            self.create_stats_response(message.payload.key)

    # todo
    def create_stats_response(self, key, store=True, update=True, forward=True):
        meta = self.get_meta_message(u"stats-response")
        self._logger.error("sending stats: %s" % self._dispersy._statistics.bartercast)
        stat = json.dumps(self._dispersy._statistics.bartercast)
        message = meta.impl(authentication=(self._my_member,),
                            distribution=(self.claim_global_time(),),
                            payload=(key, stat))
        self._dispersy.store_update_forward([message], store, update, forward)

    def check_stats_response(self, messages):
        for message in messages:
            allowed, _ = self._timeline.check(message)
            if allowed:
                yield message
            else:
                yield DelayMessageByProof(message)

    def on_stats_response(self, messages):
        for message in messages:
            self._logger.error("stats-response: %s %s %s"
                               % (message._distribution.global_time, message.payload.key, message.payload.statistic))
