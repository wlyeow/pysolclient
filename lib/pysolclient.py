from ctypes import *

from traceback import extract_stack as extract_stack, format_exc
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
# Init DLL
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
getLastErrorInfo.restype  = POINTER(ErrorInfo)

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

    @staticmethod
    def raiseExcept(codes):
        def errcheck(rc, f, args):
            if not rc in codes:
                raise SolaceError(rc, '{}(), args={}'.format(f.__name__, repr(args)))

            return rc
        return errcheck
    
    @staticmethod
    def raiseNotOK(rc, f, args):
        if rc != ReturnCode.OK:
            raise SolaceError(rc, '{}(), args={}'.format(f.__name__, repr(args)))
        return rc
    
    @staticmethod
    def returnRefParam1(rc, f, args):
        if rc == ReturnCode.NOT_FOUND:
            return None
        if rc != ReturnCode.OK:
            raise SolaceError(rc, f.__name__)

        return args[1]._obj.value

    @staticmethod
    def returnRefCharArrayAsBytes(rc, f, args):
        if rc == ReturnCode.NOT_FOUND:
            return None
        if rc != ReturnCode.OK:
            raise SolaceError(rc, f.__name__)

        return cast(args[1]._obj, POINTER(c_char * args[2]._obj.value)).contents.raw

    @staticmethod
    def returnBool(rc, f, args):
        return rc != 0

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
        self.trace = format_exc()

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

"""
_Properties class ensure only the symbolic property names get set via __setattr__().
Translation from symbolic property names to actual values get defined in the respective subclasses.
Actual translation happens at toCPropsArray and back.
"""
class _MetaProperties(type):
    def __init__(cls, name, bases, d):
        type.__init__(cls, name, bases, d)
        cls._rdict = {}
        for k, v in vars(cls).items():
            if type(v) is str:
                cls._rdict[v] = k

class _Properties(metaclass=_MetaProperties):
    def __init__(self, iterable=None, **kwargs):
        if iterable:
            for k, v in iterable:
                setattr(self, k, v)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __setattr__(self, k, v):
        if not k in vars(type(self)).keys():
            raise AttributeError('Property {} does not exist'.format(k))
        self.__dict__[k] = v
    
    def toCPropsArray(self):
        # one-liner magic is actually slower, verified with timeit!
        #
        #props = (c_char_p * (2 * len(vars(self)) + 1))(
        #        *list(map(_toBytes, chain.from_iterable(vars(self)))), None)

        def iterProps(d):
            for k, v in d.items():
                yield _toBytes(getattr(type(self), k))
                yield _toBytes(v)
                
        props = (c_char_p * (2 * len(vars(self)) + 1))( \
                *list(iterProps(vars(self))), None)
        return props

    @classmethod
    def _iterProps(cls, p):
        for idx in range(0, len(p)-1, 2):
            yield (cls._rdict[p[idx].decode()], p[idx+1].decode())

    def loadCPropsArray(self, props):
        # one-liner magic is actually slower, verified with timeit!
        #
        #return cls( zip_longest(
        #    *([ iter( map(lambda b: b.decode(), props[:-1])) ] * 2)))
        for k, v in self._iterProps(props):
            setattr(self, k, v)


class ContextProperties(_Properties):
    def __init__(self, args=None, **kw):
        if args or kw:
            super().__init__(args, **kw)
        else:
            propLen = 1
            lastProp = 1
            while lastProp is not None:
                props_t = c_char_p * propLen
                props = props_t.in_dll(_lib, '_solClient_contextPropsDefaultWithCreateThread')
                lastProp = props[-1]
                propLen += 2
            super().__init__()
            self.loadCPropsArray(props)

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

class TransactedSessionProperties(_Properties):
    HAS_PUBLISHER = "TRANSACTEDSESSION_HAS_PUBLISHER"
    CREATE_MESSAGE_DISPATCHER = "TRANSACTEDSESSION_CREATE_MESSAGE_DISPATCHER"
    REQUESTREPLY_TIMEOUT_MS = "TRANSACTEDSESSION_REQUESTREPLY_TIMEOUT_MS"
    DEFAULT_HAS_PUBLISHER = PROP_ENABLE_VAL
    DEFAULT_CREATE_MESSAGE_DISPATCHER = PROP_DISABLE_VAL
    DEFAULT_REQUESTREPLY_TIMEOUT_MS = "10000"

class FlowProperties(_Properties):
    BIND_BLOCKING = "FLOW_BIND_BLOCKING" 
    BIND_TIMEOUT_MS = "FLOW_BIND_TIMEOUT_MS" 
    BIND_ENTITY_ID = "FLOW_BIND_ENTITY_ID" 
    BIND_ENTITY_DURABLE = "FLOW_BIND_ENTITY_DURABLE" 
    BIND_NAME = "FLOW_BIND_NAME" 
    WINDOWSIZE = "FLOW_WINDOWSIZE" 
    AUTOACK = "FLOW_AUTOACK" 
    ACKMODE = "FLOW_ACKMODE" 
    TOPIC = "FLOW_TOPIC" 
    MAX_BIND_TRIES = "FLOW_MAX_BIND_TRIES" 
    ACK_TIMER_MS = "FLOW_ACK_TIMER_MS" 
    ACK_THRESHOLD = "FLOW_ACK_THRESHOLD" 
    START_STATE = "FLOW_START_STATE" 
    SELECTOR = "FLOW_SELECTOR" 
    NO_LOCAL = "FLOW_NO_LOCAL" 
    FORWARDING_MODE = "FLOW_FORWARDING_MODE" 
    MAX_UNACKED_MESSAGES = "FLOW_MAX_UNACKED_MESSAGES" 
    BROWSER = "FLOW_BROWSER" 
    ACTIVE_FLOW_IND = "FLOW_ACTIVE_FLOW_IND" 
    BIND_ENTITY_SUB = "1" 
    BIND_ENTITY_QUEUE = "2" 
    BIND_ENTITY_TE = "3" 
    BIND_ENTITY_DTE = BIND_ENTITY_TE 
    ACKMODE_AUTO = "1" 
    ACKMODE_CLIENT = "2" 
    FORWARDING_MODE_STORE_AND_FORWARD = "1" 
    FORWARDING_MODE_CUT_THROUGH = "2" 
    DEFAULT_BIND_BLOCKING = PROP_ENABLE_VAL 
    DEFAULT_BIND_TIMEOUT_MS = "10000" 
    DEFAULT_BIND_ENTITY_ID = BIND_ENTITY_SUB 
    DEFAULT_BIND_ENTITY_DURABLE = PROP_ENABLE_VAL 
    DEFAULT_BIND_NAME = "" 
    DEFAULT_WINDOWSIZE = "255" 
    DEFAULT_AUTOACK = PROP_ENABLE_VAL 
    DEFAULT_TOPIC = "" 
    DEFAULT_MAX_BIND_TRIES = "3" 
    DEFAULT_ACK_TIMER_MS = "1000" 
    DEFAULT_ACK_THRESHOLD = "60" 
    DEFAULT_START_STATE = PROP_ENABLE_VAL 
    DEFAULT_SELECTOR = "" 
    DEFAULT_NO_LOCAL = PROP_DISABLE_VAL 
    DEFAULT_FORWARDING_MODE = FORWARDING_MODE_STORE_AND_FORWARD 
    DEFAULT_MAX_UNACKED_MESSAGES = "-1" 
    DEFAULT_BROWSER = PROP_DISABLE_VAL 
    DEFAULT_ACTIVE_FLOW_IND = PROP_DISABLE_VAL 

class EndpointProperties(_Properties):
    ID = "ENDPOINT_ID" 
    NAME = "ENDPOINT_NAME" 
    DURABLE = "ENDPOINT_DURABLE" 
    PERMISSION = "ENDPOINT_PERMISSION" 
    ACCESSTYPE = "ENDPOINT_ACCESSTYPE" 
    QUOTA_MB = "ENDPOINT_QUOTA_MB" 
    MAXMSG_SIZE = "ENDPOINT_MAXMSG_SIZE" 
    RESPECTS_MSG_TTL = "ENDPOINT_RESPECTS_MSG_TTL" 
    DISCARD_BEHAVIOR = "ENDPOINT_DISCARD_BEHAVIOR" 
    MAXMSG_REDELIVERY = "ENDPOINT_MAXMSG_REDELIVERY" 
    QUEUE = "2" 
    TE = "3" 
    CLIENT_NAME = "4" 
    ACCESSTYPE_NONEXCLUSIVE = "0" 
    ACCESSTYPE_EXCLUSIVE = "1" 
    DISCARD_NOTIFY_SENDER_ON = "1" 
    DISCARD_NOTIFY_SENDER_OFF = "2" 
    DEFAULT_ID = TE 
    DEFAULT_DURABLE = PROP_ENABLE_VAL 
    DEFAULT_RESPECTS_MSG_TTL = PROP_DISABLE_VAL 
    PERM_NONE = "n"
    PERM_READ_ONLY = "r"
    PERM_CONSUME = "c"
    PERM_MODIFY_TOPIC = "m"
    PERM_DELETE = "d"

class CacheSessionProperties(_Properties):
    CACHE_NAME = "CACHESESSION_CACHE_NAME" 
    MAX_MSGS = "CACHESESSION_MAX_MSGS" 
    MAX_AGE = "CACHESESSION_MAX_AGE" 
    REQUESTREPLY_TIMEOUT_MS = "CACHESESSION_RR_TIMEOUT_MS" 
    REPLY_TO = "CACHESESSION_REPLY_TO" 
    DEFAULT_CACHE_NAME = "" 
    DEFAULT_MAX_MSGS = "1" 
    DEFAULT_MAX_AGE = "0" 
    DEFAULT_REQUESTREPLY_TIMEOUT_MS = "10000" 
    DEFAULT_REPLY_TO = "" 

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

def msgDumpToConsole(msg_p):
    Message.dumpPtr(msg_p)

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
    class _Rx_Info(Structure):
        _fields_ = [ ('callback_p', c_void_p), ('user_p', c_void_p) ]

    class _Msg_Callback(Structure):
        _fields_ = [ ('callback_p', MSG_CALLBACK_TYPE), ('user_p', c_void_p) ]
    
    class _Event_Callback(Structure):
        _fields_ = [ ('callback_p', EVENT_CALLBACK_TYPE), ('user_p', c_void_p) ]

    _fields_ = [ \
                ('rxInfo', _Rx_Info),
                ('eventInfo', _Event_Callback),
                ('rxMsgInfo', _Msg_Callback) ]

    def setMsgCallback(self, cb, user_p=None):
        self.rxMsgInfo.callback_p = MSG_CALLBACK_TYPE(cb)
        self.rxMsgInfo.user_p = cast(user_p, c_void_p)

    def setEventCallback(self, cb, user_p=None):
        self.eventInfo.callback_p = EVENT_CALLBACK_TYPE(cb)
        self.eventInfo.user_p = cast(user_p, c_void_p)


#############
# Flow
#############
"""
Same as SessionFuncInfo
"""
class FlowFuncInfo(Structure):
    class _Rx_Info(Structure):
        _fields_ = [ ('callback_p', c_void_p), ('user_p', c_void_p) ]

    class _Msg_Callback(Structure):
        _fields_ = [ ('callback_p', MSG_CALLBACK_TYPE), ('user_p', c_void_p) ]
    
    class _Event_Callback(Structure):
        _fields_ = [ ('callback_p', EVENT_CALLBACK_TYPE), ('user_p', c_void_p) ]

    _fields_ = [ \
                ('rxInfo', _Rx_Info),
                ('eventInfo', _Event_Callback),
                ('rxMsgInfo', _Msg_Callback) ]

    def setMsgCallback(self, cb, user_p=None):
        self.rxMsgInfo.callback_p = MSG_CALLBACK_TYPE(cb)
        self.rxMsgInfo.user_p = cast(user_p, c_void_p)

    def setEventCallback(self, cb, user_p=None):
        self.eventInfo.callback_p = EVENT_CALLBACK_TYPE(cb)
        self.eventInfo.user_p = cast(user_p, c_void_p)

class Flow:

    _create = _lib.solClient_session_createFlow
    _create.argtypes = [POINTER(c_char_p), c_void_p, c_void_p, POINTER(FlowFuncInfo), c_size_t]
    _create.restype  = c_int
    _create.errcheck = ReturnCode.raiseExcept((ReturnCode.OK, ReturnCode.IN_PROGRESS))
    def __init__(self, session, fprops, funcInfo = None):
        if funcInfo is None:
            funcInfo = FlowFuncInfo()
            funcInfo.setMsgCallback(_defaultMsgCallback)
            funcInfo.setEventCallback(_defaultEventCallback)
        self._pt = c_void_p()
        self.session = session
        self.funcInfo = funcInfo
        self._create(fprops.toCPropsArray(), session._pt, byref(self._pt), pointer(funcInfo), sizeof(funcInfo))

    _start = _lib.solClient_flow_start
    _start.argtypes = [c_void_p]
    _start.restype  = c_int
    _start.errcheck = ReturnCode.raiseNotOK
    def start(self):
        return self._start(self._pt)
    
    _stop = _lib.solClient_flow_stop
    _stop.argtypes = [c_void_p]
    _stop.restype  = c_int
    _stop.errcheck = ReturnCode.raiseNotOK
    def stop(self):
        return self._stop(self._pt)

    _ack = _lib.solClient_flow_sendAck
    _ack.argtypes = [c_void_p, c_uint64]
    _ack.restype  = c_int
    _ack.errcheck = ReturnCode.raiseNotOK
    def ack(self, msgId):
        _ack(self._pt, msgId)

    @classmethod
    def ackPtr(cls, flow_p, msg_p):
        cls._ack(flow_p, Message.getMsgPtrId(msg_p))

    _destroy = _lib.solClient_flow_destroy
    _destroy.argtypes = [c_void_p]
    _destroy.restype  = c_int
    _destroy.errcheck = ReturnCode.raiseNotOK
    def __del__(self):
        try:
            self._destroy(byref(self._pt))
        except SolaceError as e:
            LOG.log( LOG.ERROR, str(e) )
            _lib.solClient_resetLastErrorInfo()

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

    _create = _lib.solClient_session_create
    _create.argtypes = [POINTER(c_char_p), c_void_p, c_void_p, POINTER(SessionFuncInfo), c_size_t]
    _create.restype  = c_int
    _create.errcheck = ReturnCode.raiseNotOK
    def __init__(self, context, props, funcInfo = None):
        if funcInfo is None:
            funcInfo = SessionFuncInfo()
            funcInfo.setMsgCallback(_defaultMsgCallback)
            funcInfo.setEventCallback(_defaultEventCallback)

        self._pt = c_void_p()
        self.context = context
        self.funcInfo = funcInfo

        self._create(props.toCPropsArray(), context._pt, byref(self._pt),
                pointer(self.funcInfo), sizeof(funcInfo))

    _connect = _lib.solClient_session_connect
    _connect.argtypes = [c_void_p]
    _connect.restype  = c_int
    _connect.errcheck = ReturnCode.raiseExcept((ReturnCode.OK, ReturnCode.IN_PROGRESS))
    def connect(self):
        return self._connect(self._pt)

    _createTempTopic = _lib.solClient_session_createTemporaryTopicName
    _createTempTopic.argtypes = [c_void_p, c_char_p, c_size_t]
    _createTempTopic.restype  = c_int
    _createTempTopic.errcheck = ReturnCode.returnRefCharArrayAsBytes
    def createTempTopic(self):
        return

    _disconnect = _lib.solClient_session_disconnect
    _disconnect.argtypes = [c_void_p]
    _disconnect.restype  = c_int
    _disconnect.errcheck = ReturnCode.raiseNotOK
    def disconnect(self):
        return self._disconnect(self._pt)

    _sendMsg = _lib.solClient_session_sendMsg
    _sendMsg.argtypes = [c_void_p, c_void_p]
    _sendMsg.restype  = c_int
    _sendMsg.errcheck = ReturnCode.raiseExcept((ReturnCode.OK, ReturnCode.WOULD_BLOCK))
    def sendMsg(self, msg):
        return self._sendMsg(self._pt, msg._pt)
    
    _topicSub = _lib.solClient_session_topicSubscribe
    _topicSub.argtypes = [c_void_p, c_char_p]
    _topicSub.restype  = c_int
    _topicSub.errcheck = ReturnCode.raiseExcept((ReturnCode.OK, ReturnCode.WOULD_BLOCK, ReturnCode.IN_PROGRESS))
    _topicSubExt = _lib.solClient_session_topicSubscribeExt
    _topicSubExt.argtypes = [c_void_p, c_uint32, c_char_p]
    _topicSubExt.restype  = c_int
    _topicSubExt.errcheck = ReturnCode.raiseExcept((ReturnCode.OK, ReturnCode.WOULD_BLOCK, ReturnCode.IN_PROGRESS))
    def topicSubscribe(self, topic, flags = None):
        if flags is not None:
            return self._topicSubExt(self._pt, flags, topic.encode())
        else:
            return self._topicSub(self._pt, topic.encode())

    def topicSubscribeDispatch(self, topic, flags, dispatchFunc, user):
        pass

    _epProvision = _lib.solClient_session_endpointProvision
    _epProvision.argtypes = [POINTER(c_char_p), c_void_p, c_int, c_void_p, c_char_p, c_size_t]
    _epProvision.restype  = c_int
    _epProvision.errcheck = ReturnCode.raiseExcept((ReturnCode.OK, ReturnCode.IN_PROGRESS, ReturnCode.WOULD_BLOCK))
    def epProvision(self, epprops, flags = ProvisionFlags.WAITFORCONFIRM, corrTag = None):
        return self._epProvision(epprops.toCPropsArray(), self._pt, flags, corrTag, None, 0)

    _destroy = _lib.solClient_session_destroy
    _destroy.argtypes = [c_void_p]
    _destroy.restype  = c_int
    _destroy.errcheck = ReturnCode.raiseNotOK
    def __del__(self):
        try:
            self._destroy(byref(self._pt))
        except SolaceError as e:
            LOG.log( LOG.ERROR, str(e) )
            _lib.solClient_resetLastErrorInfo()

class TransactedSession:
    MAX_SESSION_NAME_LENGTH = 64

# Dest
class Destination(Structure):
    _fields_ = [ ('destType', c_int), ('dest', c_char_p) ]

    # ENUM destination types
    (NULL, TOPIC, QUEUE, TOPIC_TEMP, QUEUE_TEMP) = range(-1, 4)

    def __init__(self, dest=None, destType=TOPIC):
        super().__init__(destType, _toBytes(dest))

    def __eq__(self, other):
        for fld in self._fields_:
            if getattr(self, fld[0]) != getattr(other, fld[0]):
                return False
        return True

    def __ne__(self, other):
        for fld in self._fields_:
            if getattr(self, fld[0]) != getattr(other, fld[0]):
                return True
        return False

    def setDest(self, d):
        self.dest = _toBytes(d)

# Message
class Message:
    (COS_1, COS_2, COS_3) = range(3)
    (DELIVERY_MODE_DIRECT, DELIVERY_MODE_PERSISTENT, DELIVERY_MODE_NONPERSISTENT) = ( 0x00, 0x10, 0x20 )

    _alloc = _lib.solClient_msg_alloc
    _alloc.argtypes = [c_void_p]
    _alloc.restype  = c_int
    _alloc.errcheck = ReturnCode.raiseNotOK
    def __init__(self, pt = None):
        if pt is None:
            self._pt = c_void_p()
            self._alloc(byref(self._pt))
        else:
            self._pt = cast(pt, c_void_p)

    _setAppMsgId = _lib.solClient_msg_setApplicationMessageId
    _setAppMsgId.argtypes = [c_void_p, c_char_p]
    _setAppMsgId.restype  = c_int
    _setAppMsgId.errcheck = ReturnCode.raiseNotOK
    def setAppMsgId(self, id):
        self._setAppMsgId(self._pt, _toBytes(id))

    _setBinaryAttachment = _lib.solClient_msg_setBinaryAttachment
    _setBinaryAttachment.argtypes = [c_void_p, c_void_p, c_uint32]
    _setBinaryAttachment.restype  = c_int
    _setBinaryAttachment.errcheck = ReturnCode.raiseNotOK
    def setBinaryAttachment(self, bytes):
        # bytes are copied into the message
        self._setBinaryAttachment(self._pt, bytes, 0 if bytes is None else len(bytes))

    _setCOS = _lib.solClient_msg_setClassOfService
    _setCOS.argtypes = [c_void_p, c_uint32]
    _setCOS.restype  = c_int
    _setCOS.errcheck = ReturnCode.raiseNotOK
    def setCOS(self, cos):
        self._setCOS(self._pt, c_uint32(cos))

    _setCorrId = _lib.solClient_msg_setCorrelationId
    _setCorrId.argtypes = [c_void_p, c_char_p]
    _setCorrId.restype  = c_int
    _setCorrId.errcheck = ReturnCode.raiseNotOK
    def setCorrId(self, corrId):
        self._setCorrId(self._pt, _toBytes(corrId))

    _setCorrTagPtr = _lib.solClient_msg_setCorrelationTagPtr
    _setCorrTagPtr.argtypes = [c_void_p, c_void_p, c_size_t]
    _setCorrTagPtr.restype  = c_int
    _setCorrTagPtr.errcheck = ReturnCode.raiseNotOK
    def setCorrTag(self, tag):
        self.corrTag = tag
        self._setCorrTagPtr(self._pt, byref(self.corrTag), sizeof(self.corrTag))

    _setDTO = _lib.solClient_msg_setDeliverToOne
    _setDTO.argtypes = [c_void_p, c_ubyte]
    _setDTO.restype  = c_int
    _setDTO.errcheck = ReturnCode.raiseNotOK
    def setDTO(self, dto):
        self._setDTO(self._pt, c_ubyte(1 if dto else 0))

    _setDelivery = _lib.solClient_msg_setDeliveryMode
    _setDelivery.argtypes = [c_void_p, c_uint32]
    _setDelivery.restype  = c_int
    _setDelivery.errcheck = ReturnCode.raiseNotOK
    def setDelivery(self, mode):
        self._setDelivery(self._pt, c_uint32(mode))

    _setDest = _lib.solClient_msg_setDestination
    _setDest.argtypes = [c_void_p, POINTER(Destination), c_size_t]
    _setDest.restype  = c_int
    _setDest.errcheck = ReturnCode.raiseNotOK
    def setDest(self, d):
        self._setDest(self._pt, pointer(d), sizeof(d))

    _setDMQ = _lib.solClient_msg_setDMQEligible
    _setDMQ.argtypes = [c_void_p, c_ubyte]
    _setDMQ.restype  = c_int
    _setDMQ.errcheck = ReturnCode.raiseNotOK
    def setDMQ(self, dmq):
        self._setDMQ(self._pt, c_ubyte(1 if dmq else 0))

    _setEliding = _lib.solClient_msg_setElidingEligible
    _setEliding.argtypes = [c_void_p, c_ubyte]
    _setEliding.restype  = c_int
    _setEliding.errcheck = ReturnCode.raiseNotOK
    def setEliding(self, elide):
        self._setEliding(self._pt, c_ubyte(1 if elide else 0))

    _setReplyTo = _lib.solClient_msg_setReplyTo
    _setReplyTo.argtypes = [c_void_p, POINTER(Destination), c_size_t]
    _setReplyTo.restype  = c_int
    _setReplyTo.errcheck = ReturnCode.raiseNotOK
    def setReplyTo(self, d):
        self._setReplyTo(self._pt, pointer(d), sizeof(d))

    _setSenderId = _lib.solClient_msg_setSenderId
    _setSenderId.argtypes = [c_void_p, c_char_p]
    _setSenderId.restype  = c_int
    _setSenderId.errcheck = ReturnCode.raiseNotOK
    def setSenderId(self, id):
        self._setSenderId(self._pt, _toBytes(id))

    _setSenderTimestamp = _lib.solClient_msg_setSenderTimestamp
    _setSenderTimestamp.argtypes = [c_void_p, c_int64]
    _setSenderTimestamp.restype  = c_int
    _setSenderTimestamp.errcheck = ReturnCode.raiseNotOK
    def setSenderTimestamp(self, ts):
        self._setSenderTimestamp(self._pt, c_int64(ts))

    _setSeqNum = _lib.solClient_msg_setSequenceNumber
    _setSeqNum.argtypes = [c_void_p, c_int64]
    _setSeqNum.restype  = c_int
    _setSeqNum.errcheck = ReturnCode.raiseNotOK
    def setSeqNum(self, n):
        self._setSeqNum(self._pt, c_int64(n))

    _setTTL = _lib.solClient_msg_setTimeToLive
    _setTTL.argtypes = [c_void_p, c_int64]
    _setTTL.restype  = c_int
    _setTTL.errcheck = ReturnCode.raiseNotOK
    def setTTL(self, ttl):
        self._setTTL(self._pt, c_int64(ttl))

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

    _getAppMsgId = _lib.solClient_msg_getApplicationMessageId
    _getAppMsgId.argtypes = [c_void_p, POINTER(c_char_p)]
    _getAppMsgId.restype  = c_int
    _getAppMsgId.errcheck = ReturnCode.returnRefParam1
    def getAppMsgId(self):
        return self._getAppMsgId(self._pt, byref(c_char_p())).decode()

    _getBinaryAttachment = _lib.solClient_msg_getBinaryAttachmentPtr
    _getBinaryAttachment.argtypes = [c_void_p, c_void_p, POINTER(c_uint32)]
    _getBinaryAttachment.restype  = c_int
    _getBinaryAttachment.errcheck = ReturnCode.returnRefCharArrayAsBytes
    def getBinaryAttachment(self):
        return self._getBinaryAttachment(self._pt, byref(c_void_p()), byref(c_uint32()))

    _getCacheStatus = _lib.solClient_msg_isCacheMsg
    _getCacheStatus.argtypes = [c_void_p]
    _getCacheStatus.restype  = c_int
    _getCacheStatus.errcheck = ReturnCode.returnRefParam1
    def getCacheStatus(self):
        return self._getCacheStatus(self._pt)

    _getCOS = _lib.solClient_msg_getClassOfService
    _getCOS.argtypes = [c_void_p, POINTER(c_uint32)]
    _getCOS.restype  = c_int
    _getCOS.errcheck = ReturnCode.returnRefParam1
    def getCOS(self):
        return self._getCOS(self._pt, byref(c_uint32()))

    _getDest = _lib.solClient_msg_getDestination
    _getDest.argtypes = [c_void_p, POINTER(Destination), c_size_t]
    _getDest.restype  = c_int
    _getDest.errcheck = ReturnCode.returnRefParam1
    def getDest(self):
        return self._getDest(self._pt, byref(Destination()), sizeof(Destination))

    _getMsgId = _lib.solClient_msg_getMsgId
    _getMsgId.argtypes = [c_void_p, POINTER(c_uint64)]
    _getMsgId.restype  = c_int
    _getMsgId.errcheck = ReturnCode.returnRefParam1
    def getMsgId(self):
        return self._getMsgId(self._pt, byref(c_uint64()))

    @classmethod
    def getMsgPtrId(cls, msg_p):
        return cls._getMsgId(msg_p, byref(c_uint64()))

    _getSeqNum = _lib.solClient_msg_getSequenceNumber
    _getSeqNum.argtypes = [c_void_p, POINTER(c_int64)]
    _getSeqNum.restype  = c_int
    _getSeqNum.errcheck = ReturnCode.returnRefParam1
    def getSeqNum(self):
        return self._getSeqNum(self._pt, byref(c_int64()))

    _getTTL = _lib.solClient_msg_getTimeToLive
    _getTTL.argtypes = [c_void_p, POINTER(c_int64)]
    _getTTL.restype  = c_int
    _getTTL.errcheck = ReturnCode.returnRefParam1
    def getTTL(self):
        return self._getTTL(self._pt, byref(c_int64()))

    _isDiscardIndicated = _lib.solClient_msg_isDiscardIndication
    _isDiscardIndicated.argtypes = [c_void_p]
    _isDiscardIndicated.restype  = c_ubyte
    _isDiscardIndicated.errcheck = ReturnCode.returnBool
    def isDiscardIndicated(self):
        return self._isDiscardIndicated(self._pt)

    _isDTO = _lib.solClient_msg_isDeliverToOne
    _isDTO.argtypes = [c_void_p]
    _isDTO.restype  = c_ubyte
    _isDTO.errcheck = ReturnCode.returnBool
    def isDTO(self):
        return self._isDTO(self._pt)

    _isDMQ = _lib.solClient_msg_isDMQEligible
    _isDMQ.argtypes = [c_void_p]
    _isDMQ.restype  = c_ubyte
    _isDMQ.errcheck = ReturnCode.returnBool
    def isDMQ(self):
        return self._isDMQ(self._pt)

    _isEliding = _lib.solClient_msg_isElidingEligible
    _isEliding.argtypes = [c_void_p]
    _isEliding.restype  = c_ubyte
    _isEliding.errcheck = ReturnCode.returnBool
    def isEliding(self):
        return self._isEliding(self._pt)

    _isRedelivered = _lib.solClient_msg_isRedelivered
    _isRedelivered.argtypes = [c_void_p]
    _isRedelivered.restype  = c_ubyte
    _isRedelivered.errcheck = ReturnCode.returnBool
    def isRedelivered(self):
        return self._isRedelivered(self._pt)

    _isReplyMsg = _lib.solClient_msg_isReplyMsg
    _isReplyMsg.argtypes = [c_void_p]
    _isReplyMsg.restype  = c_ubyte
    _isReplyMsg.errcheck = ReturnCode.returnBool
    def isReplyMsg(self):
        return self._isReplyMsg(self._pt)

    _dump = _lib.solClient_msg_dump
    _dump.argtypes = [c_void_p, c_void_p, c_size_t]
    _dump.restype  = c_int
    _dump.errcheck = ReturnCode.raiseNotOK
    def dump(self, buffer=None):
        self._dump(self._pt, buffer, 0 if buffer is None else len(buffer))

    @classmethod
    def dumpPtr(cls, msg_p, buffer=None):
        cls._dump(msg_p, buffer, 0 if buffer is None else len(buffer))

    _free = _lib.solClient_msg_free
    _free.argtypes = [ c_void_p ]
    _free.restype  = c_int
    _free.errcheck = ReturnCode.raiseNotOK
    def __del__(self):
        try:
            self._free(byref(self._pt))
        except SolaceError as e:
            LOG.log( LOG.ERROR, str(e) )
            _lib.solClient_resetLastErrorInfo()

# init, set to error
_lib.solClient_initialize( LOG.ERROR, c_void_p() )

def cleanup():
    _lib.solClient_cleanup()

import atexit
atexit.register(cleanup)
