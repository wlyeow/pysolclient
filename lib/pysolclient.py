from ctypes import *

from traceback import extract_stack as extract_stack
from functools import singledispatch

import inspect
import os.path

# ENUM callback types
(CALLBACK_OK, CALLBACK_TAKE_MSG) = [0,1]

# ENUM context timer
(CONTEXT_TIMER_ONE_SHOT, CONTEXT_TIMER_REPEAT) = [0, 1]

# ENUM dispatch 
DISPATCH_TYPE_CALLBACK = 1

# Enable, Disable
(PROP_DISABLE_VAL, PROP_ENABLE_VAL) = ("0", "1")

# Some Props
SOLCLIENT_MODIFYPROP_FLAGS_WAITFORCONFIRM = (0x01)
SOLCLIENT_TRANSPORT_PROTOCOL_NULL = ("")
SOLCLIENT_SESSION_SEND_MULTIPLE_LIMIT = 50
SOLCLIENT_MAX_SELECTOR_SIZE = (1023)

@singledispatch
def _toBytes(b):
    return repr(b).encode()
_toBytes.register(bytes, lambda b: b)
_toBytes.register(str, lambda s: s.encode())
_toBytes.register(type(None), lambda b: None)

##############
# Init Module
##############

from ctypes.util import find_library
_library_name = find_library('libsolclient')
if _library_name:
    _lib = cdll.LoadLibrary(_library_name)
else:
    raise ImportError('libsolclient not found')

##############
# functions
##############

# getLastErrorInfo()
class ErrorInfo(Structure):
    STR_SIZE = 256
    _fields_ = [ ('subCode', c_int), ('responseCode', c_uint32), ('errorStr', c_char * STR_SIZE) ]

getLastErrorInfo = _lib.solClient_getLastErrorInfo
getLastErrorInfo.argtypes = []
getLastErrorInfo.restype = POINTER(ErrorInfo)

class SubscribeFlags:
    LOCAL_DISPATCH_ONLY = 0x08
    REQUEST_CONFIRM = 0x10
    RX_ALL_DELIVER_TO_ONE = 0x04
    WAITFORCONFIRM = 0x02

class ProvisionFlags:
    IGNORE_EXIST_ERRORS = 0x02
    WAITFORCONFIRM = 0x01

class SessionEvent:
    # ENUM session events
    (UP_NOTICE, DOWN_ERROR, CONNECT_FAILED_ERROR, REJECTED_MSG_ERROR, SUBSCRIPTION_ERROR, RX_MSG_TOO_BIG_ERROR, ACKNOWLEDGEMENT, ASSURED_PUBLISHING_UP, ASSURED_CONNECT_FAILED, ASSURED_DELIVERY_DOWN, TE_UNSUBSCRIBE_ERROR, DTE_UNSUBSCRIBE_ERROR, TE_UNSUBSCRIBE_OK, DTE_UNSUBSCRIBE_OK, CAN_SEND, RECONNECTING_NOTICE, RECONNECTED_NOTICE, PROVISION_ERROR, PROVISION_OK, SUBSCRIPTION_OK, VIRTUAL_ROUTER_NAME_CHANGED, MODIFYPROP_OK, MODIFYPROP_FAIL, REPUBLISH_UNACKED_MESSAGES) = list(range(8)) + [8, 8, 9, 9, 10, 10] + list(range(11,21))
    
    _toString = _lib.solClient_session_eventToString
    _toString.argtypes = [ c_int ]
    _toString.restype = c_char_p

    @classmethod
    def toString(cls, event):
        return cls._toString(event).decode()

class ReturnCode:
    # ENUM return codes
    (FAIL, OK, WOULD_BLOCK, IN_PROGRESS, NOT_READY, EOS, NOT_FOUND, NOEVENT, INCOMPLETE, ROLLBACK) = range(-1,9)

    _toString = _lib.solClient_returnCodeToString
    _toString.argtypes = [ c_int ]
    _toString.restype = c_char_p

    @classmethod
    def toString(cls, event):
        return cls._toString(event).decode()
    
class SubCode:
    # ENUM subcodes 1
    (OK, PARAM_OUT_OF_RANGE, PARAM_NULL_PTR, PARAM_CONFLICT, INSUFFICIENT_SPACE, OUT_OF_RESOURCES, INTERNAL_ERROR, OUT_OF_MEMORY, PROTOCOL_ERROR, INIT_NOT_CALLED, TIMEOUT, KEEP_ALIVE_FAILURE, SESSION_NOT_ESTABLISHED, OS_ERROR, COMMUNICATION_ERROR, USER_DATA_TOO_LARGE, TOPIC_TOO_LARGE, INVALID_TOPIC_SYNTAX, XML_PARSE_ERROR, LOGIN_FAILURE, INVALID_VIRTUAL_ADDRESS, CLIENT_DELETE_IN_PROGRESS, TOO_MANY_CLIENTS, SUBSCRIPTION_ALREADY_PRESENT, SUBSCRIPTION_NOT_FOUND, SUBSCRIPTION_INVALID, SUBSCRIPTION_OTHER, CONTROL_OTHER, DATA_OTHER, LOG_FILE_ERROR, MESSAGE_TOO_LARGE, SUBSCRIPTION_TOO_MANY, INVALID_SESSION_OPERATION, TOPIC_MISSING, ASSURED_MESSAGING_NOT_ESTABLISHED, ASSURED_MESSAGING_STATE_ERROR, QUEUENAME_TOPIC_CONFLICT, QUEUENAME_TOO_LARGE, QUEUENAME_INVALID_MODE, MAX_TOTAL_MSGSIZE_EXCEEDED, DBLOCK_ALREADY_EXISTS, NO_STRUCTURED_DATA, CONTAINER_BUSY, INVALID_DATA_CONVERSION, CANNOT_MODIFY_WHILE_NOT_IDLE, MSG_VPN_NOT_ALLOWED, CLIENT_NAME_INVALID, MSG_VPN_UNAVAILABLE, CLIENT_USERNAME_IS_SHUTDOWN, DYNAMIC_CLIENTS_NOT_ALLOWED, CLIENT_NAME_ALREADY_IN_USE, CACHE_NO_DATA, CACHE_SUSPECT_DATA, CACHE_ERROR_RESPONSE, CACHE_INVALID_SESSION, CACHE_TIMEOUT, CACHE_LIVEDATA_FULFILL, CACHE_ALREADY_IN_PROGRESS, MISSING_REPLY_TO) = range(59)
    
    # ENUM subcodes 2
    (INVALID_TOPIC_NAME_FOR_TE, INVALID_TOPIC_NAME_FOR_DTE, UNKNOWN_QUEUE_NAME, UNKNOWN_TE_NAME, UNKNOWN_DTE_NAME, MAX_CLIENTS_FOR_QUEUE, MAX_CLIENTS_FOR_TE, MAX_CLIENTS_FOR_DTE) = [ 60, 60, 61, 62, 62, 63, 64, 64 ]
    
    # ENUM subcodes 3
    (UNEXPECTED_UNBIND, QUEUE_NOT_FOUND, CLIENT_ACL_DENIED, SUBSCRIPTION_ACL_DENIED, PUBLISH_ACL_DENIED, DELIVER_TO_ONE_INVALID, SPOOL_OVER_QUOTA, QUEUE_SHUTDOWN, TE_SHUTDOWN, NO_MORE_NON_DURABLE_QUEUE_OR_TE, ENDPOINT_ALREADY_EXISTS, PERMISSION_NOT_ALLOWED, INVALID_SELECTOR, MAX_MESSAGE_USAGE_EXCEEDED, ENDPOINT_PROPERTY_MISMATCH, SUBSCRIPTION_MANAGER_DENIED, UNKNOWN_CLIENT_NAME, QUOTA_OUT_OF_RANGE, SUBSCRIPTION_ATTRIBUTES_CONFLICT, INVALID_SMF_MESSAGE, NO_LOCAL_NOT_SUPPORTED, UNSUBSCRIBE_NOT_ALLOWED_CLIENTS_BOUND, CANNOT_BLOCK_IN_CONTEXT, FLOW_ACTIVE_FLOW_INDICATION_UNSUPPORTED, UNRESOLVED_HOST, CUT_THROUGH_UNSUPPORTED, CUT_THROUGH_ALREADY_BOUND, CUT_THROUGH_INCOMPATIBLE_WITH_SESSION, INVALID_FLOW_OPERATION, UNKNOWN_FLOW_NAME, REPLICATION_IS_STANDBY, LOW_PRIORITY_MSG_CONGESTION, LIBRARY_NOT_LOADED, FAILED_LOADING_TRUSTSTORE, UNTRUSTED_CERTIFICATE, UNTRUSTED_COMMONNAME, CERTIFICATE_DATE_INVALID, FAILED_LOADING_CERTIFICATE_AND_KEY, BASIC_AUTHENTICATION_IS_SHUTDOWN, CLIENT_CERTIFICATE_AUTHENTICATION_IS_SHUTDOWN, UNTRUSTED_CLIENT_CERTIFICATE, CLIENT_CERTIFICATE_DATE_INVALID, CACHE_REQUEST_CANCELLED, DELIVERY_MODE_UNSUPPORTED, PUBLISHER_NOT_CREATED, FLOW_UNBOUND, INVALID_TRANSACTED_SESSION_ID, INVALID_TRANSACTION_ID, MAX_TRANSACTED_SESSIONS_EXCEEDED, TRANSACTED_SESSION_NAME_IN_USE, SERVICE_UNAVAILABLE, NO_TRANSACTION_STARTED, PUBLISHER_NOT_ESTABLISHED, MESSAGE_PUBLISH_FAILURE, TRANSACTION_FAILURE, MESSAGE_CONSUME_FAILURE, ENDPOINT_MODIFIED, INVALID_CONNECTION_OWNER, KERBEROS_AUTHENTICATION_IS_SHUTDOWN, COMMIT_OR_ROLLBACK_IN_PROGRESS, UNBIND_RESPONSE_LOST, MAX_TRANSACTIONS_EXCEEDED, COMMIT_STATUS_UNKNOWN, PROXY_AUTH_REQUIRED, PROXY_AUTH_FAILURE, NO_SUBSCRIPTION_MATCH) = range(65,131)

    _toString = _lib.solClient_subCodeToString
    _toString.argtypes = [ c_int ]
    _toString.restype = c_char_p

    @classmethod
    def toString(cls, subcode):
        return cls._toString(subcode).decode()

#########
# Errors
#########

class SolaceError(Exception):
    def __init__(self, rc, msg):
        self.msg = msg
        self.rc = rc
        
        info_p = getLastErrorInfo()
        self.subCode = info_p.contents.subCode
        self.responseCode = info_p.contents.responseCode
        self.errorStr = info_p.contents.errorStr.decode()

        # format the message
        message = '{} - ReturnCode="{}", SubCode="{}", ResponseCode={}, Info="{}"\n'.format(self.msg,
                ReturnCode.toString(self.rc),
                SubCode.toString(self.subCode),
                self.responseCode, self.errorStr)

        super().__init__(message)

class LOG:
    # ENUM log levels
    (EMERGENCY, ALERT, CRITICAL, ERROR, WARNING, NOTICE, INFO, DEBUG) = range(8)

    # ENUM log categories
    (CATEGORY_ALL, CATEGORY_SDK, CATEGORY_APP) = range(3)
    
    _solClient_log_appFilterLevel_g = c_int.in_dll(_lib, '_solClient_log_appFilterLevel_g')
    _solClient_log_output_detail = _lib._solClient_log_output_detail
    _solClient_log_output_detail.restype = None

    # setFilter()
    setFilterLevel = _lib.solClient_log_setFilterLevel
    setFilterLevel.argypes = [ c_int, c_int ]
    setFilterLevel.restype = c_int

    # log()
    @classmethod
    def log(cls, level, formatStr):
        if level <= cls._solClient_log_appFilterLevel_g.value:
            trace = extract_stack(limit=2)[0]
            filename = '/' + os.path.basename(trace.filename)
            cls._solClient_log_output_detail(cls.CATEGORY_APP, level, 
                    filename.encode(), trace.lineno, formatStr.encode())

# printLastError()
def printLastError(rc, errorStr):
    info_p = getLastErrorInfo()
    LOG.log ( LOG.ERROR,
            '{} - ReturnCode="{}", SubCode="{}", ResponseCode={}, Info="{}"\n'.format(errorStr,
                ReturnCode.toString(rc),
                SubCode.toString(info_p.contents.subCode),
                info_p.contents.responseCode,
                info_p.contents.errorStr.decode()) )

    _lib.solClient_resetLastErrorInfo()


############
# Properties
############

from collections.abc import MutableMapping
#from itertools import chain, zip_longest

class _Properties(MutableMapping):
    def __init__(self, *args, **kw):
        self._dict = dict(*args, **kw)
    def __getitem__(self, key):
        return self._dict[key]
    def __iter__(self):
        return iter(self._dict)
    def __len__(self):
        return len(self._dict)
    def __setitem__(self, key, value):
        self._dict[key] = value
    def __delitem__(self, key):
        del self._dict[key]

    def toCPropsArray(self):
        # one-liner magic is actually slower, verified with timeit!
        #
        #props = (c_char_p * (2 * len(self._dict) + 1))(
        #        *list(map(_toBytes, chain.from_iterable(self._dict.items()))), None)
        
        def iterProps(d):
            for k, v in d.items():
                yield _toBytes(k)
                yield _toBytes(v)

        props = (c_char_p * (2 * len(self._dict) + 1))(
                *list(iterProps(self._dict)), None)

        return props

    @classmethod
    def fromCPropsArray(cls, props):
        # one-liner magic is actually slower, verified with timeit!
        #
        #return cls( zip_longest(
        #    *([ iter( map(lambda b: b.decode(), props[:-1])) ] * 2)))

        def iterProps(p):
            for idx in range(0, len(p)-1, 2):
                yield (p[idx].decode(), p[idx+1].decode())

        return cls(iterProps(props))

class ContextProperties(_Properties):
    def __init__(self, *args, **kw):
        if args or kw:
            super().__init__(*args, **kw)
        else:
            propLen = 1
            lastProp = 1
            while lastProp is not None:
                props_t = c_char_p * propLen
                props = props_t.in_dll(_lib, '_solClient_contextPropsDefaultWithCreateThread')
                lastProp = props[-1]
                propLen += 2
            super().__init__(super().fromCPropsArray(props))

    # context property defines
    TIME_RES_MS = "CONTEXT_TIME_RES_MS"
    CREATE_THREAD = "CONTEXT_CREATE_THREAD"
    THREAD_AFFINITY = "CONTEXT_THREAD_AFFINITY"
    DEFAULT_TIME_RES_MS = "50"
    DEFAULT_CREATE_THREAD = PROP_DISABLE_VAL
    DEFAULT_THREAD_AFFINITY = "0"

class SessionProperties(_Properties):
    ACK_EVENT_MODE_PER_MSG = "SESSION_ACK_EVENT_MODE_PER_MSG"
    ACK_EVENT_MODE_WINDOWED = "SESSION_ACK_EVENT_MODE_WINDOWED"
    USERNAME = "SESSION_USERNAME"
    PASSWORD = "SESSION_PASSWORD"
    HOST = "SESSION_HOST"
    PORT = "SESSION_PORT"
    BUFFER_SIZE = "SESSION_BUFFER_SIZE"
    CONNECT_BLOCKING = "SESSION_CONNECT_BLOCKING"
    SEND_BLOCKING = "SESSION_SEND_BLOCKING"
    SUBSCRIBE_BLOCKING = "SESSION_SUBSCRIBE_BLOCKING"
    BLOCK_WHILE_CONNECTING = "SESSION_BLOCK_WHILE_CONNECTING"
    BLOCKING_WRITE_TIMEOUT_MS = "SESSION_WRITE_TIMEOUT_MS"
    CONNECT_TIMEOUT_MS = "SESSION_CONNECT_TIMEOUT_MS"
    SUBCONFIRM_TIMEOUT_MS = "SESSION_SUBCONFIRM_TIMEOUT_MS"
    IGNORE_DUP_SUBSCRIPTION_ERROR = "SESSION_IGNORE_DUP_SUBSCRIPTION_ERROR"
    TCP_NODELAY = "SESSION_TCP_NODELAY"
    SOCKET_SEND_BUF_SIZE = "SESSION_SOCKET_SEND_BUF_SIZE"
    SOCKET_RCV_BUF_SIZE = "SESSION_SOCKET_RCV_BUF_SIZE"
    KEEP_ALIVE_INT_MS = "SESSION_KEEP_ALIVE_INTERVAL_MS"
    KEEP_ALIVE_LIMIT = "SESSION_KEEP_ALIVE_LIMIT"
    APPLICATION_DESCRIPTION = "SESSION_APPLICATION_DESCRIPTION"
    CLIENT_MODE = "SESSION_CLIENT_MODE"
    BIND_IP = "SESSION_BIND_IP"
    PUB_WINDOW_SIZE = "SESSION_PUB_WINDOW_SIZE"
    PUB_ACK_TIMER = "SESSION_PUB_ACK_TIMER"
    VPN_NAME = "SESSION_VPN_NAME"
    VPN_NAME_IN_USE = "SESSION_VPN_NAME_IN_USE"
    CLIENT_NAME = "SESSION_CLIENT_NAME"
    SUBSCRIBER_LOCAL_PRIORITY = "SESSION_SUBSCRIBER_LOCAL_PRIORITY"
    SUBSCRIBER_NETWORK_PRIORITY = "SESSION_SUBSCRIBER_NETWORK_PRIORITY"
    COMPRESSION_LEVEL = "SESSION_COMPRESSION_LEVEL"
    GENERATE_RCV_TIMESTAMPS = "SESSION_RCV_TIMESTAMP"
    GENERATE_SEND_TIMESTAMPS = "SESSION_SEND_TIMESTAMP"
    GENERATE_SENDER_ID = "SESSION_SEND_SENDER_ID"
    GENERATE_SEQUENCE_NUMBER = "SESSION_SEND_SEQUENCE_NUMBER"
    CONNECT_RETRIES_PER_HOST = "SESSION_CONNECT_RETRIES_PER_HOST"
    CONNECT_RETRIES = "SESSION_CONNECT_RETRIES"
    RECONNECT_RETRIES = "SESSION_RECONNECT_RETRIES"
    RECONNECT_RETRY_WAIT_MS = "SESSION_RECONNECT_RETRY_WAIT_MS"
    USER_ID = "SESSION_USER_ID"
    P2PINBOX_IN_USE = "SESSION_REPLY_TO_DEFAULT_DEST"
    REPLY_TO_DEFAULT_DEST = P2PINBOX_IN_USE
    REAPPLY_SUBSCRIPTIONS = "SESSION_REAPPLY_SUBSCRIPTIONS"
    TOPIC_DISPATCH = "SESSION_TOPIC_DISPATCH"
    PROVISION_TIMEOUT_MS = "SESSION_PROVISION_TIMEOUT_MS"
    CALCULATE_MESSAGE_EXPIRATION = "SESSION_CALCULATE_MESSAGE_EXPIRATION"
    VIRTUAL_ROUTER_NAME = "SESSION_VIRTUAL_ROUTER_NAME"
    NO_LOCAL = "SESSION_NO_LOCAL"
    AD_PUB_ROUTER_WINDOWED_ACK = "SESSION_AD_PUB_ROUTER_WINDOWED_ACK"
    MODIFYPROP_TIMEOUT_MS = "SESSION_MODIFYPROP_TIMEOUT_MS"
    ACK_EVENT_MODE = "SESSION_ACK_EVENT_MODE"
    SSL_EXCLUDED_PROTOCOLS = "SESSION_SSL_EXCLUDED_PROTOCOLS"
    SSL_VALIDATE_CERTIFICATE = "SESSION_SSL_VALIDATE_CERTIFICATE"
    SSL_CLIENT_CERTIFICATE_FILE = "SESSION_SSL_CLIENT_CERTIFICATE_FILE"
    SSL_CLIENT_PRIVATE_KEY_FILE = "SESSION_SSL_CLIENT_PRIVATE_KEY_FILE"
    SSL_CLIENT_PRIVATE_KEY_FILE_PASSWORD = "SESSION_SSL_CLIENT_PRIVATE_KEY_FILE_PASSWORD"
    SSL_CONNECTION_DOWNGRADE_TO = "SESSION_SSL_CONNECTION_DOWNGRADE_TO"
    AUTHENTICATION_SCHEME = "SESSION_AUTHENTICATION_SCHEME"
    KRB_SERVICE_NAME = "SESSION_KRB_SERVICE_NAME"
    UNBIND_FAIL_ACTION = "SESSION_UNBIND_FAIL_ACTION"
    WEB_TRANSPORT_PROTOCOL = ("SESSION_WEB_TRANSPORT_PROTOCOL")
    WEB_TRANSPORT_PROTOCOL_IN_USE = ("SESSION_WEB_TRANSPORT_PROTOCOL_IN_USE")
    WEB_TRANSPORT_PROTOCOL_LIST = ("SESSION_WEB_TRANSPORT_PROTOCOL_LIST")
    TRANSPORT_PROTOCOL_DOWNGRADE_TIMEOUT_MS = ("SESSION_TRANSPORT_PROTOCOL_DOWNGRADE_TIMEOUT_MS")
    GD_RECONNECT_FAIL_ACTION = "SESSION_GD_RECONNECT_FAIL_ACTION"
    AUTHENTICATION_SCHEME_BASIC = "AUTHENTICATION_SCHEME_BASIC"
    AUTHENTICATION_SCHEME_CLIENT_CERTIFICATE = "AUTHENTICATION_SCHEME_CLIENT_CERTIFICATE"
    AUTHENTICATION_SCHEME_GSS_KRB = "AUTHENTICATION_SCHEME_GSS_KRB"
    UNBIND_FAIL_ACTION_RETRY = "UNBIND_FAIL_ACTION_RETRY"
    UNBIND_FAIL_ACTION_DISCONNECT = "UNBIND_FAIL_ACTION_DISCONNECT"
    SSL_VALIDATE_CERTIFICATE_DATE = "SESSION_SSL_VALIDATE_CERTIFICATE_DATE"
    SSL_CIPHER_SUITES = "SESSION_SSL_CIPHER_SUITES"
    SSL_TRUST_STORE_DIR = "SESSION_SSL_TRUST_STORE_DIR"
    SSL_TRUSTED_COMMON_NAME_LIST = "SESSION_SSL_TRUSTED_COMMON_NAME_LIST"
    GD_RECONNECT_FAIL_ACTION_AUTO_RETRY = ("GD_RECONNECT_FAIL_ACTION_AUTO_RETRY")
    GD_RECONNECT_FAIL_ACTION_DISCONNECT = ("GD_RECONNECT_FAIL_ACTION_DISCONNECT")
    DEFAULT_USERNAME = ""
    DEFAULT_PASSWORD = ""
    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = "55555"
    DEFAULT_PORT_COMPRESSION = "55003"
    DEFAULT_PORT_SSL = "55443"
    DEFAULT_BUFFER_SIZE = "90000"
    DEFAULT_CONNECT_BLOCKING = PROP_ENABLE_VAL
    DEFAULT_SEND_BLOCKING = PROP_ENABLE_VAL
    DEFAULT_SUBSCRIBE_BLOCKING = PROP_ENABLE_VAL
    DEFAULT_BLOCK_WHILE_CONNECTING = PROP_ENABLE_VAL
    DEFAULT_BLOCKING_WRITE_TIMEOUT_MS = "100000"
    DEFAULT_CONNECT_TIMEOUT_MS = "30000"
    DEFAULT_SUBCONFIRM_TIMEOUT_MS = "10000"
    DEFAULT_IGNORE_DUP_SUBSCRIPTION_ERROR = PROP_ENABLE_VAL
    DEFAULT_TCP_NODELAY = PROP_ENABLE_VAL
    DEFAULT_SOCKET_SEND_BUF_SIZE = "90000"
    DEFAULT_SOCKET_RCV_BUF_SIZE = "150000"
    DEFAULT_KEEP_ALIVE_INT_MS = "3000"
    DEFAULT_KEEP_ALIVE_LIMIT = "3"
    DEFAULT_APPLICATION_DESCRIPTION = ""
    DEFAULT_CLIENT_MODE = PROP_DISABLE_VAL
    DEFAULT_BIND_IP = ""
    DEFAULT_PUB_ACK_TIMER = "2000"
    DEFAULT_PUB_WINDOW_SIZE = "50"
    DEFAULT_VPN_NAME = ""
    DEFAULT_CLIENT_NAME = ""
    DEFAULT_SUBSCRIBER_LOCAL_PRIORITY = "1"
    DEFAULT_SUBSCRIBER_NETWORK_PRIORITY = "1"
    DEFAULT_COMPRESSION_LEVEL = "0"
    DEFAULT_GENERATE_RCV_TIMESTAMPS = PROP_DISABLE_VAL
    DEFAULT_GENERATE_SEND_TIMESTAMPS = PROP_DISABLE_VAL
    DEFAULT_GENERATE_SENDER_ID = PROP_DISABLE_VAL
    DEFAULT_GENERATE_SEQUENCE_NUMBER = PROP_DISABLE_VAL
    DEFAULT_CONNECT_RETRIES_PER_HOST = "0"
    DEFAULT_CONNECT_RETRIES = "0"
    DEFAULT_RECONNECT_RETRIES = "0"
    DEFAULT_RECONNECT_RETRY_WAIT_MS = "3000"
    DEFAULT_REAPPLY_SUBSCRIPTIONS = PROP_DISABLE_VAL
    DEFAULT_TOPIC_DISPATCH = PROP_DISABLE_VAL
    DEFAULT_PROVISION_TIMEOUT_MS = "3000"
    DEFAULT_MODIFYPROP_TIMEOUT_MS = "10000"
    DEFAULT_CALCULATE_EXPIRATION_TIME = PROP_DISABLE_VAL
    DEFAULT_NO_LOCAL = PROP_DISABLE_VAL
    DEFAULT_AD_PUB_ROUTER_WINDOWED_ACK = PROP_ENABLE_VAL
    DEFAULT_SSL_EXCLUDED_PROTOCOLS = ""
    DEFAULT_SSL_VALIDATE_CERTIFICATE = PROP_ENABLE_VAL
    DEFAULT_SSL_VALIDATE_CERTIFICATE_DATE = PROP_ENABLE_VAL
    DEFAULT_SSL_CIPHER_SUITES = ("ECDHE-RSA-AES256-GCM-SHA384,ECDHE-RSA-AES256-SHA384,ECDHE-RSA-AES256-SHA,AES256-GCM-SHA384,AES256-SHA256,AES256-SHA,ECDHE-RSA-DES-CBC3-SHA,DES-CBC3-SHA,ECDHE-RSA-AES128-GCM-SHA256,ECDHE-RSA-AES128-SHA256,ECDHE-RSA-AES128-SHA,AES128-GCM-SHA256,AES128-SHA256,AES128-SHA,RC4-SHA,RC4-MD5")
    DEFAULT_AUTHENTICATION_SCHEME = AUTHENTICATION_SCHEME_BASIC
    DEFAULT_KRB_SERVICE_NAME = "solace"
    DEFAULT_UNBIND_FAIL_ACTION = UNBIND_FAIL_ACTION_RETRY
    DEFAULT_WEB_TRANSPORT_PROTOCOL = SOLCLIENT_TRANSPORT_PROTOCOL_NULL
    DEFAULT_TRANSPORT_PROTOCOL_DOWNGRADE_TIMEOUT_MS = ("3000")
    DEFAULT_GD_RECONNECT_FAIL_ACTION = GD_RECONNECT_FAIL_ACTION_AUTO_RETRY
    SSL_CIPHER_ECDHE_RSA_AES256_GCM_SHA384 = ("ECDHE-RSA-AES256-GCM-SHA384")
    SSL_CIPHER_TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 = ("TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384")
    SSL_CIPHER_ECDHE_RSA_AES256_SHA384 = ("ECDHE-RSA-AES256-SHA384")
    SSL_CIPHER_TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384 = ("TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384")
    SSL_CIPHER_ECDHE_RSA_AES256_SHA = ("ECDHE-RSA-AES256-SHA")
    SSL_CIPHER_TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA = ("TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA")
    SSL_CIPHER_AES256_GCM_SHA384 = ("AES256-GCM-SHA384")
    SSL_CIPHER_TLS_RSA_WITH_AES_256_GCM_SHA384 = ("TLS_RSA_WITH_AES_256_GCM_SHA384")
    SSL_CIPHER_AES256_SHA256 = ("AES256-SHA256")
    SSL_CIPHER_TLS_RSA_WITH_AES_256_CBC_SHA256 = ("TLS_RSA_WITH_AES_256_CBC_SHA256")
    SSL_CIPHER_AES256_SHA = ("AES256-SHA")
    SSL_CIPHER_TLS_RSA_WITH_AES_256_CBC_SHA = ("TLS_RSA_WITH_AES_256_CBC_SHA")
    SSL_CIPHER_ECDHE_RSA_DES_CBC3_SHA = ("ECDHE-RSA-DES-CBC3-SHA")
    SSL_CIPHER_TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA = ("TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA")
    SSL_CIPHER_DES_CBC3_SHA = ("DES-CBC3-SHA")
    SSL_CIPHER_SSL_RSA_WITH_3DES_EDE_CBC_SHA = ("SSL_RSA_WITH_3DES_EDE_CBC_SHA")
    SSL_CIPHER_ECDHE_RSA_AES128_GCM_SHA256 = ("ECDHE-RSA-AES128-GCM-SHA256")
    SSL_CIPHER_TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 = ("TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256")
    SSL_CIPHER_ECDHE_RSA_AES128_SHA256 = ("ECDHE-RSA-AES128-SHA256")
    SSL_CIPHER_TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256 = ("TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256")
    SSL_CIPHER_ECDHE_RSA_AES128_SHA = ("ECDHE-RSA-AES128-SHA")
    SSL_CIPHER_TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA = ("TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA")
    SSL_CIPHER_AES128_GCM_SHA256 = ("AES128-GCM-SHA256")
    SSL_CIPHER_TLS_RSA_WITH_AES_128_GCM_SHA256 = ("TLS_RSA_WITH_AES_128_GCM_SHA256")
    SSL_CIPHER_AES128_SHA256 = ("AES128-SHA256")
    SSL_CIPHER_TLS_RSA_WITH_AES_128_CBC_SHA256 = ("TLS_RSA_WITH_AES_128_CBC_SHA256")
    SSL_CIPHER_AES128_SHA = ("AES128-SHA")
    SSL_CIPHER_TLS_RSA_WITH_AES_128_CBC_SHA = ("TLS_RSA_WITH_AES_128_CBC_SHA")
    SSL_CIPHER_RC4_SHA = ("RC4-SHA")
    SSL_CIPHER_SSL_RSA_WITH_RC4_128_SHA = ("SSL_RSA_WITH_RC4_128_SHA")
    SSL_CIPHER_RC4_MD5 = ("RC4-MD5")
    SSL_CIPHER_SSL_RSA_WITH_RC4_128_MD5 = ("SSL_RSA_WITH_RC4_128_MD5")
    SSL_PROTOCOL_TLSV1_2 = ("TLSv1.2")
    SSL_PROTOCOL_TLSV1_1 = ("TLSv1.1")
    SSL_PROTOCOL_TLSV1 = ("TLSv1")
    SSL_PROTOCOL_SSLV3 = ("SSLv3")
    MAX_USERNAME_LEN = (189)
    MAX_PASSWORD_LEN = (128)
    MAX_HOSTS = (16)
    MAX_APP_DESC = (255)
    MAX_CLIENT_NAME_LEN = (160)
    MAX_VPN_NAME_LEN = (32)
    MAX_VIRTUAL_ROUTER_NAME_LEN = (52)

class TransactedSessionProperties(_Properties):
    HAS_PUBLISHER = "TRANSACTEDSESSION_HAS_PUBLISHER"
    CREATE_MESSAGE_DISPATCHER = "TRANSACTEDSESSION_CREATE_MESSAGE_DISPATCHER"
    REQUESTREPLY_TIMEOUT_MS = "TRANSACTEDSESSION_REQUESTREPLY_TIMEOUT_MS"
    DEFAULT_HAS_PUBLISHER = PROP_ENABLE_VAL
    DEFAULT_CREATE_MESSAGE_DISPATCHER = PROP_DISABLE_VAL
    DEFAULT_REQUESTREPLY_TIMEOUT_MS = "10000"

##############
# ContextInfo
##############

class ContextFuncInfo(Structure):
    class RegFDFuncInfo(Structure):
        FD_CALLBACK_FUNC = CFUNCTYPE( None, c_void_p, c_int, c_uint32, c_void_p )
        REG_FD_FUNC = CFUNCTYPE( c_int, c_void_p, c_int, c_uint32, FD_CALLBACK_FUNC, c_void_p )
        UNREG_FD_FUNC = CFUNCTYPE( c_int, c_void_p, c_int, c_uint32 )

        _fields_ = [    ('regFdFuncInfo', REG_FD_FUNC),
                        ('unregFdFuncInfo', UNREG_FD_FUNC),
                        ('user_p', c_void_p) ]

    _fields_ = [ ('regFdInfo', RegFDFuncInfo) ]

###########
# Context
###########

class Context:
    def __init__(self, props = None, funcInfo = None):
        if props is None:
            props = ContextProperties()
        if funcInfo is None:
            self.contextFuncInfo = ContextFuncInfo()
        else:
            self.contextFuncInfo = funcInfo

        self._pt = c_void_p()
        
        rc = _lib.solClient_context_create(
                props.toCPropsArray(), byref(self._pt),
                pointer(self.contextFuncInfo), sizeof(self.contextFuncInfo))

        if rc != ReturnCode.OK:
            raise SolaceError(rc, "context.create")

    def __del__(self):
        rc = _lib.solClient_context_destroy(byref(self._pt))

        if rc != ReturnCode.OK:
            printLastError(rc, "context.destroy")

################
# Callbacks
################

MSG_CALLBACK_TYPE = CFUNCTYPE(c_int, c_void_p, c_void_p, c_void_p)

def msgDumpToConsole( msg_p ):
    _lib.solClient_msg_dump( msg_p, c_void_p(), 0 )

def _defaultMsgCallback( session_p, msg_p, user_p ):
    msgDumpToConsole(msg_p)
    return CALLBACK_OK

class EventCallbackInfo(Structure):
    _fields_ = [ \
                    ('sessionEvent', c_int),
                    ('responseCode', c_uint32),
                    ('info_p', c_char_p),
                    ('correlation_p', c_void_p) ]

EVENT_CALLBACK_TYPE = CFUNCTYPE(None, c_void_p, POINTER(EventCallbackInfo), c_void_p)

def _defaultEventCallback( session_p, eventInfo_p, user_p ):
    event = eventInfo_p.contents.sessionEvent

    if event == SessionEvent.UP_NOTICE or \
        event == SessionEvent.ACKNOWLEDGEMENT or \
        event == SessionEvent.TE_UNSUBSCRIBE_OK or \
        event == SessionEvent.CAN_SEND or \
        event == SessionEvent.RECONNECTING_NOTICE or \
        event == SessionEvent.RECONNECTED_NOTICE or \
        event == SessionEvent.PROVISION_OK or \
        event == SessionEvent.SUBSCRIPTION_OK:

            LOG.log(LOG.INFO, '_defaultEventCallback - {}\n'.format(
                SessionEvent.toString(event)))

    elif event == SessionEvent.DOWN_ERROR or \
        event == SessionEvent.CONNECT_FAILED_ERROR or \
        event == SessionEvent.REJECTED_MSG_ERROR or \
        event == SessionEvent.SUBSCRIPTION_ERROR or \
        event == SessionEvent.RX_MSG_TOO_BIG_ERROR or \
        event == SessionEvent.TE_UNSUBSCRIBE_ERROR or \
        event == SessionEvent.PROVISION_ERROR:

            info_p = getLastErrorInfo()
            
            LOG.log(LOG.ERROR,
                    '_defaultEventCallback - {}; subCode {}, responseCode {}, reason {}\n'.format(
                        SessionEvent.toString(event),
                        SubCode.toString( info_p.contents.subCode ),
                        info_p.contents.responseCode,
                        info_p.contents.errorStr.decode()) )
    
    else:
        LOG.log(LOG.ERROR,
                '_defaultEventCallback - {}; Unrecognized or deprecated event.\n'.format(
                    SessionEvent.toString(event)))
    

###############
# SessionInfo
###############

class SessionFuncInfo(Structure):
    class _Msg_Callback(Structure):
        _fields_ = [ ('callback_p', MSG_CALLBACK_TYPE), ('user_p', c_void_p) ]
    
    class _Event_Callback(Structure):
        _fields_ = [ ('callback_p', EVENT_CALLBACK_TYPE), ('user_p', c_void_p) ]

    _fields_ = [ \
                ('rxInfo', (c_void_p * 2)),
                ('eventInfo', _Event_Callback),
                ('rxMsgInfo', _Msg_Callback) ]

#############
# Session
#############

class Session:
    PEER_PLATFORM = "SESSION_PEER_PLATFORM"
    PEER_PORT_SPEED = "SESSION_PEER_PORT_SPEED"
    PEER_PORT_TYPE = "SESSION_PEER_PORT_TYPE"
    PEER_ROUTER_NAME = "SESSION_PEER_ROUTER_NAME"
    PEER_SOFTWARE_DATE = "SESSION_PEER_SOFTWARE_DATE"
    PEER_SOFTWARE_VERSION = "SESSION_PEER_SOFTWARE_VERSION"

    def __init__(self, context, props, funcInfo = None):
        if funcInfo is None:
            funcInfo = SessionFuncInfo()
            funcInfo.rxMsgInfo.callback_p = MSG_CALLBACK_TYPE(_defaultMsgCallback)
            funcInfo.eventInfo.callback_p = EVENT_CALLBACK_TYPE(_defaultEventCallback)

        self._pt = c_void_p()
        self.context = context
        self.funcInfo = funcInfo
        self.props = props

        rc = _lib.solClient_session_create ( self.props.toCPropsArray(), context._pt, byref(self._pt),
                pointer(self.funcInfo), sizeof(funcInfo))

        if rc != ReturnCode.OK:
            raise SolaceError(rc, "session.create")

    def connect(self):
        rc = _lib.solClient_session_connect(self._pt)

        # no thorough checks on blocking or not
        if rc != ReturnCode.OK and rc != ReturnCode.IN_PROGRESS:
            raise SolaceError(rc, "session.connect")
        return rc

    def disconnect(self):
        rc = _lib.solClient_session_disconnect(self._pt)
        
        if rc != ReturnCode.OK:
            raise SolaceError(rc, "session.disconnect")

    def sendMsg(self, msg):
        rc = _lib.solClient_session_sendMsg(self._pt, msg._pt)

        if rc != ReturnCode.OK and rc != ReturnCode.WOULD_BLOCK:
            raise SolaceError(rc, "session.sendMsg")
        return rc
    
    def topicSubscribe(self, topic, flags = None):
        if flags is not None:
            rc = _lib.solClient_session_topicSubscribe(self._pt, topic.encode())
        else:
            rc = _lib.solClient_session_topicSubscribeExt(self._pt, flags, topic.encode())

        if rc != ReturnCode.OK and rc != ReturnCode.WOULD_BLOCK and rc != ReturnCode.IN_PROGRESS:
            raise SolaceError(rc, "session.topicSubscribe")

    def topicSubscribeDispatch(self, topic, flags, dispatchFunc, user):
        pass

    def __del__(self):
        rc = _lib.solClient_session_destroy(byref(self._pt))

        if rc != ReturnCode.OK:
            printLastError(rc, "session.destroy")

class TransactedSession:
    MAX_SESSION_NAME_LENGTH = 64

# Dest
class Destination(Structure):
    _fields_ = [ ('destType', c_int), ('dest', c_char_p) ]

    # ENUM destination types
    (NULL, TOPIC, QUEUE, TOPIC_TEMP, QUEUE_TEMP) = range(-1, 4)

    def __init__(self, dest=None, destType=TOPIC):
        super().__init__(destType, _toBytes(dest))

    def setDest(self, d):
        self.dest = _toBytes(d)

# Message
class Message:
    (COS_1, COS_2, COS_3) = range(3)
    (DELIVERY_MODE_DIRECT, DELIVERY_MODE_PERSISTENT, DELIVERY_MODE_NONPERSISTENT) = ( 0x00, 0x10, 0x20 )

    def __init__(self):
        self._pt = c_void_p()
        rc = _lib.solClient_msg_alloc(byref(self._pt))

        if rc != ReturnCode.OK:
            raise SolaceError(rc, "msg.alloc")

    def setAppMsgId(self, id):
        rc = _lib.solClient_msg_setApplicationMessageId(self._pt, _toBytes(id))

        if rc != ReturnCode.OK:
            raise SolaceError(rc, "msg.setAppMsgId")

    def setBinaryAttachment(self, bytes):
        # bytes are copied into the message
        rc = _lib.solClient_msg_setBinaryAttachment(self._pt, bytes, len(bytes))

        if rc != ReturnCode.OK:
            raise SolaceError(rc, "msg.setBinAttach")

    def setCOS(self, cos):
        rc = _lib.solClient_msg_setClassOfService(self._pt, c_uint32(cos))

        if rc != ReturnCode.OK:
            raise SolaceError(rc, "msg.setCOS")

    def setCorrId(self, corrId):
        rc = _lib.solClient_msg_setCorrelationId(self._pt, _toBytes(corrId))

        if rc != ReturnCode.OK:
            raise SolaceError(rc, "msg.setCorrId")

    def setDTO(self, dto):
        rc = _lib.solClient_msg_setDeliverToOne(self._pt, c_ubyte(1 if dto else 0))

        if rc != ReturnCode.OK:
            raise SolaceError(rc, "msg.setDTO")

    def setDelivery(self, mode):
        rc = _lib.solClient_msg_setDeliveryMode(self._pt, c_uint32(mode))

        if rc != ReturnCode.OK:
            raise SolaceError(rc, "msg.setDelivery")

    def setDest(self, d):
        rc = _lib.solClient_msg_setDestination(self._pt, pointer(d), sizeof(d))

        if rc != ReturnCode.OK:
            raise SolaceError(rc, "msg.setDestination")

    def setDMQ(self, dmq):
        rc = _lib.solClient_msg_setDMQEligible(self._pt, c_ubyte(1 if dmq else 0))

        if rc != ReturnCode.OK:
            raise SolaceError(rc, "msg.setDMQ")

    def setEliding(self, elide):
        rc = _lib.solClient_msg_setElidingEligible(self._pt, c_ubyte(1 if elide else 0))

        if rc != ReturnCode.OK:
            raise SolaceError(rc, "msg.setEliding")

    def setReplyTo(self, d):
        rc = _lib.solClient_msg_setReplyTo(self._pt, pointer(d), sizeof(d))

        if rc != ReturnCode.OK:
            raise SolaceError(rc, "msg.setReplyTo")

    def setSenderId(self, id):
        rc = _lib.solClient_msg_setSenderId(self._pt, _toBytes(id))

        if rc != ReturnCode.OK:
            raise SolaceError(rc, "msg.setSenderId")

    def setSenderTimestamp(self, ts):
        rc = _lib.solClient_msg_setSenderTimestamp(self._pt, c_int64(ts))

        if rc != ReturnCode.OK:
            raise SolaceError(rc, "msg.setSenderId")

    def setSeqNum(self, n):
        rc = _lib.solClient_msg_setSequenceNumber(self._pt, c_int64(ts))

        if rc != ReturnCode.OK:
            raise SolaceError(rc, "msg.setSeqNum")

    def setTTL(self, ttl):
        rc = _lib.solClient_msg_setTimeToLive(self._pt, c_int64(ttl))

        if rc != ReturnCode.OK:
            raise SolaceError(rc, "msg.setTTL")

    def applyProps(self, **kwargs):
        setMethods = dict(inspect.getmembers(self, predicate=\
                lambda f: inspect.ismethod(f) and f.__name__[:3] == 'set'))

        errors = {}
        for name, value in kwargs.items():
            try:
                setMethods['set'+name](value)
            except Exception as e:
                errors[name] = e

        return errors

    def __del__(self):
        rc = _lib.solClient_msg_free(byref(self._pt))

        if rc != ReturnCode.OK:
            printLastError(rc, "msg.free")

# init, set to error
_lib.solClient_initialize( LOG.ERROR, c_void_p() )

def cleanup():
    _lib.solClient_cleanup()

import atexit
atexit.register(cleanup)
