#!/usr/bin/env python3

from pysolclient import *
from pysolclient import _defaultMsgCallback
from pysolclient import _defaultEventCallback
import common
import sys
import time

#setup
conf = common.init('t')

context = Context()
sprops = SessionProperties(HOST=conf.host, VPN_NAME=conf.user.vpn, USERNAME=conf.user.name)

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

print('Subscribe to {}.'.format(conf.topic))
session.topicSubscribe(conf.topic)

msg = Message()
err = msg.applyProps( \
        Dest=Destination(conf.topic),
        BinaryAttachment='Hello World!\n'.encode(),
        Delivery=Message.DELIVERY_MODE_DIRECT)

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
