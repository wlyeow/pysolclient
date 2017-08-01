#!/usr/bin/env python3

from pysolclient import *
import sys

def main_run():
    context = Context()
    
    sprops = SessionProperties(HOST=sys.argv[1], VPN_NAME=sys.argv[2])
    sprops.USERNAME = sys.argv[3]
    
    session = Session(context, sprops)
    session.connect()
    
    msg = Message()
    msg.setDest(Destination(sys.argv[4]))
    msg.setBinaryAttachment('Hello World!\n'.encode())
    
    session.sendMsg(msg)
    print('Message sent.')
    
    session.disconnect()

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('Usage: {} <ip> <vpn> <username> <topic>'.format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)
    
    LOG.setFilterLevel(LOG.CATEGORY_APP, LOG.INFO)
    main_run()
