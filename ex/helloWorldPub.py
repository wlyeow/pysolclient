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

session = solclient.Session(context, sprops)
session.connect()

msg = solclient.Message()
msg.setDestination(solclient.Destination(sys.argv[4]))
msg.setBinaryAttachment('Hello World!\n'.encode())

session.sendMsg(msg)
print('Message sent.')

session.disconnect()

del msg
del session
del context
