__author__ = 'davidshaw'

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


SYNC_STATE = enum("STOP", "START", "OPTIONS", "FOLDER_SYNC", "PROVISION", "QUEUE_SYNC",
                  "RESET_SYNC", "RUN_LOOP", "QUEUE_PING", "HTTP_ERROR")

STATE_STATUS = enum("SUCCESS", "NETWORK_ERROR", "USER_FIX", "ADMIN_FIX")

EAS_TYPES = enum("ExchangeServer2010SP1", "ExchangeServer2010",
                 "ExchangeServer2007SP1", "ExchangeServer2007",
                 "ExchangeServer2003SP2")

EXCHANGE_VERSIONS = {
    EAS_TYPES.ExchangeServer2010SP1: "14.1",
    EAS_TYPES.ExchangeServer2010: "14.0",
    EAS_TYPES.ExchangeServer2007SP1: "12.1",
    EAS_TYPES.ExchangeServer2007: "12.0",
    EAS_TYPES.ExchangeServer2003SP2: "2.5"
}

EXCHANGE_PROTOCOL_ORDER = [
        EXCHANGE_VERSIONS[EAS_TYPES.ExchangeServer2010SP1],
        EXCHANGE_VERSIONS[EAS_TYPES.ExchangeServer2010],
        EXCHANGE_VERSIONS[EAS_TYPES.ExchangeServer2007SP1],
        EXCHANGE_VERSIONS[EAS_TYPES.ExchangeServer2007],
        EXCHANGE_VERSIONS[EAS_TYPES.ExchangeServer2003SP2]
        ]
