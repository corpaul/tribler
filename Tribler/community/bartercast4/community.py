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
    @classmethod
    def get_master_members(cls, dispersy):
# generated: Thu Oct 30 12:59:19 2014
# curve: NID_sect571r1
# len: 571 bits ~ 144 bytes signature
# pub: 170 3081a7301006072a8648ce3d020106052b81040027038192000405ef988346197abe009065e6f9f517263063495554e4d278074feb1be3e81586b44f90b8a11f170f0a059d8f26c259118e6afc775f3d1e7c46462c9de0ec2bb94e480390622056b002c1f121acc52c18a0857ce59e79cf73642a4787fcdc5398d332000fbd44b16f14b005c0910d81cb85392fd036f32a242044c8263e0c6b9dc10b68f9c30540cfbd8a6bb5ccec786e
# pub-sha1 59accbc05521d8b894e8e6ef8d686411384cdec9
#-----BEGIN PUBLIC KEY-----
# MIGnMBAGByqGSM49AgEGBSuBBAAnA4GSAAQF75iDRhl6vgCQZeb59RcmMGNJVVTk
# 0ngHT+sb4+gVhrRPkLihHxcPCgWdjybCWRGOavx3Xz0efEZGLJ3g7Cu5TkgDkGIg
# VrACwfEhrMUsGKCFfOWeec9zZCpHh/zcU5jTMgAPvUSxbxSwBcCRDYHLhTkv0Dbz
# KiQgRMgmPgxrncELaPnDBUDPvYprtczseG4=
#-----END PUBLIC KEY-----
        master_key = "3081a7301006072a8648ce3d020106052b81040027038192000405ef988346197abe009065e6f9f517263063495554e4d278074feb1be3e81586b44f90b8a11f170f0a059d8f26c259118e6afc775f3d1e7c46462c9de0ec2bb94e480390622056b002c1f121acc52c18a0857ce59e79cf73642a4787fcdc5398d332000fbd44b16f14b005c0910d81cb85392fd036f32a242044c8263e0c6b9dc10b68f9c30540cfbd8a6bb5ccec786e".decode("HEX")
        master = dispersy.get_member(public_key=master_key)
        return [master]

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

    def initialize(self, integrate_with_tribler=False, auto_join_channel=False):
        super(BarterCommunity, self).initialize()

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
        # self._dispersy.store_update_forward([message], store, update, forward)

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
        # records = self._dispersy._statistics.bartercast
        print "REAL STATS: %s" % self._dispersy._statistics.bartercast
        records = ["peerid1", 123, "peerid2", 456]
        message = meta.impl(authentication=(self._my_member,),
                            distribution=(self.claim_global_time(),),
                            destination=(candidate,),
                            payload=(stats_type, records))
        self._dispersy._forward([message])
        # self._dispersy.store_update_forward([message], store, update, forward)

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
