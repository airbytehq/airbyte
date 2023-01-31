from enum import Enum


class CampaignStatus(Enum):
    ACTIVE = 'active'
    STOPPED = 'stopped'
    PAUSED = 'paused'
    ALL = 'all'


class CampaignType(Enum):
    RTB = 'rtb'
    VAST = 'vast'
    ALL = 'all'


class AccountAuthMethod(Enum):
    AGENCY = "agency"
    ACCOUNT = "account"
