#!/usr/bin/env python3

import solclient
import sys

if len(sys.argv) < 5:
    print('Usage: {} <ip> <vpn> <username> <topic>'.format(sys.argv[0]), file=sys.stderr)
    sys.exit(1)

solclient.LOG.setFilterLevel(
        solclient.LOG.CATEGORY_APP,
        solclient.LOG.INFO)

context = solclient.Context()

sprops = solclient.SessionProperties()
sprops[ solclient.SessionProperties.HOST ] = sys.argv[1]
sprops[ solclient.SessionProperties.VPN_NAME ] = sys.argv[2]
sprops[ solclient.SessionProperties.USERNAME ] = sys.argv[3]

rxMsg = 0
def rxMsgCallback( session_p, msg_p, user_p ):
    global rxMsg
    rxMsg += 1
    print('Message received.')
    solclient._defaultMsgCallback(session_p, msg_p, user_p)

    return solclient.CALLBACK_OK

funcInfo = solclient.SessionFuncInfo()
funcInfo.rxMsgInfo.callback_p = solclient.MSG_CALLBACK_TYPE(rxMsgCallback)
funcInfo.eventInfo.callback_p = solclient.EVENT_CALLBACK_TYPE(solclient._defaultEventCallback)

session = solclient.Session(context, sprops, funcInfo)
session.connect()

print('Subscribe to {}.'.format(sys.argv[4]))
session.topicSubscribe(sys.argv[4])

import time
while rxMsg < 1:
    time.sleep(1)

session.disconnect()
