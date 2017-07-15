#!/usr/bin/env python3

from pysolclient import *
from pysolclient import _defaultMsgCallback
from pysolclient import _defaultEventCallback
import sys

if len(sys.argv) < 5:
    print('Usage: {} <ip> <vpn> <username> <topic>'.format(sys.argv[0]), file=sys.stderr)
    sys.exit(1)

LOG.setFilterLevel(
        LOG.CATEGORY_APP,
        LOG.INFO)

context = Context()

sprops = SessionProperties(HOST=sys.argv[1], VPN_NAME=sys.argv[2], USERNAME=sys.argv[3])

rxMsg = 0
def rxMsgCallback( session_p, msg_p, user_p ):
    global rxMsg
    rxMsg += 1
    print('Message received.')
    _defaultMsgCallback(session_p, msg_p, user_p)

    return CALLBACK_OK

funcInfo = SessionFuncInfo()
funcInfo.rxMsgInfo.callback_p = MSG_CALLBACK_TYPE(rxMsgCallback)
funcInfo.eventInfo.callback_p = EVENT_CALLBACK_TYPE(_defaultEventCallback)

session = Session(context, sprops, funcInfo)
session.connect()

print('Subscribe to {}.'.format(sys.argv[4]))
session.topicSubscribe(sys.argv[4])

import time
while rxMsg < 1:
    time.sleep(1)

session.disconnect()
