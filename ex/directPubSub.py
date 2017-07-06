#!/usr/bin/env python3

import pysolclient as solclient
import common
import sys
import time

#setup
conf = common.init('t')

context = solclient.Context()

sprops = solclient.SessionProperties()
sprops[ solclient.SessionProperties.HOST ] = conf.host
sprops[ solclient.SessionProperties.VPN_NAME ] = conf.user.vpn
sprops[ solclient.SessionProperties.USERNAME ] = conf.user.name

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

print('Subscribe to {}.'.format(conf.topic))
session.topicSubscribe(conf.topic)

msg = solclient.Message()
err = msg.applyProps( \
        Dest=solclient.Destination(conf.topic),
        BinaryAttachment='Hello World!\n'.encode(),
        Delivery=solclient.Message.DELIVERY_MODE_DIRECT)

if err:
    for n, e in err.items():
        print('Cannot set {}:\t{}: {}'.format(n, type(e).__name__, str(e)))
    raise RuntimeError('Cannot continue')

session.sendMsg(msg)
print('Message sent.')
del msg

time.sleep(0.1)
while rxMsg < 1:
    time.sleep(1)

session.disconnect()
