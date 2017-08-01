#!/usr/bin/env python3

from pysolclient import *
from pysolclient import _defaultMsgCallback
import sys

def main():
    context = Context()
    sprops = SessionProperties(HOST=sys.argv[1], VPN_NAME=sys.argv[2], USERNAME=sys.argv[3])
    
    def eventCallback(session_p, eventInfo_p, user_p):
        if eventInfo_p.contents.sessionEvent == SessionEvent.UP_NOTICE:
            print('Session Up!')
        elif eventInfo_p.contents.sessionEvent == SessionEvent.ACKNOWLEDGEMENT:
            print('Got an ACK!')

    funcInfo = SessionFuncInfo()
    funcInfo.setMsgCallback(_defaultMsgCallback)
    funcInfo.setEventCallback(eventCallback)

    session = Session(context, sprops, funcInfo)
    session.connect()
    
    msg = Message()
    msg.setDest(Destination(sys.argv[4], Destination.QUEUE))
    msg.setDelivery(Message.DELIVERY_MODE_PERSISTENT)
    msg.setBinaryAttachment('Hello World!\n'.encode())

    session.sendMsg(msg)
    print('Message sent.')
    del msg
    
    import time
    time.sleep(2)
    
    session.disconnect()

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('Usage: {} <ip> <vpn> <username> <queue>'.format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)
    
    LOG.setFilterLevel(LOG.CATEGORY_APP, LOG.INFO)
    main()
