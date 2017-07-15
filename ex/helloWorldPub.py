#!/usr/bin/env python3

from pysolclient import *
import sys

if len(sys.argv) < 5:
    print('Usage: {} <ip> <vpn> <username> <topic>'.format(sys.argv[0]), file=sys.stderr)
    sys.exit(1)

LOG.setFilterLevel(
        LOG.CATEGORY_APP,
        LOG.INFO)

context = Context()

sprops = SessionProperties(HOST=sys.argv[1], VPN_NAME=sys.argv[2])
sprops.USERNAME = sys.argv[3]
#sprops = SessionProperties()
#sprops[ SessionProperties.HOST ] = sys.argv[1]
#sprops[ SessionProperties.VPN_NAME ] = sys.argv[2]
#sprops[ SessionProperties.USERNAME ] = sys.argv[3]

session = Session(context, sprops)
session.connect()

msg = Message()
msg.setDest(Destination(sys.argv[4]))
msg.setBinaryAttachment('Hello World!\n'.encode())

session.sendMsg(msg)
print('Message sent.')

del msg

session.disconnect()
