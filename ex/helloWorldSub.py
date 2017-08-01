#!/usr/bin/env python3

from pysolclient import *
from pysolclient import _defaultMsgCallback
from pysolclient import _defaultEventCallback
import sys

def main_run():
    context = Context()
    
    sprops = SessionProperties(HOST=sys.argv[1], VPN_NAME=sys.argv[2], USERNAME=sys.argv[3])
    
    rxMsg = c_int(0)
    def rxMsgCallback( session_p, msg_p, user_p ):
        cast(user_p, POINTER(c_int)).contents.value += 1
        print('Message received.')
        _defaultMsgCallback(session_p, msg_p, None)
    
        return CALLBACK_OK
    
    funcInfo = SessionFuncInfo()
    funcInfo.setMsgCallback(rxMsgCallback, byref(rxMsg))
    funcInfo.setEventCallback(_defaultEventCallback)
    
    session = Session(context, sprops, funcInfo)
    session.connect()
    
    print('Subscribe to {}.'.format(sys.argv[4]))
    session.topicSubscribe(sys.argv[4])
    
    import time
    while rxMsg.value < 1:
        time.sleep(1)
    
    session.disconnect()

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('Usage: {} <ip> <vpn> <username> <topic>'.format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)
    
    LOG.setFilterLevel(LOG.CATEGORY_APP, LOG.INFO)
    main_run()
