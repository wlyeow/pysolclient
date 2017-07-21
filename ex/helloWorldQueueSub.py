#!/usr/bin/env python3

from pysolclient import *
from pysolclient import _defaultMsgCallback
from pysolclient import _defaultEventCallback
import sys

if len(sys.argv) < 5:
    print('Usage: {} <ip> <vpn> <username> <queue>'.format(sys.argv[0]), file=sys.stderr)
    sys.exit(1)

LOG.setFilterLevel(
        LOG.CATEGORY_ALL,
        LOG.INFO)

context = Context()
sprops = SessionProperties(HOST=sys.argv[1], VPN_NAME=sys.argv[2], USERNAME=sys.argv[3])

session = Session(context, sprops)
session.connect()

epprops = EndpointProperties(ID=EndpointProperties.QUEUE, \
        NAME=sys.argv[4], PERMISSION=EndpointProperties.PERM_DELETE, \
        QUOTA_MB="4000")

print('Provisioning endpoint {}.'.format(sys.argv[4]))
session.epProvision(epprops, ProvisionFlags.IGNORE_EXIST_ERRORS | ProvisionFlags.WAITFORCONFIRM)

fprops = FlowProperties(BIND_BLOCKING=PROP_ENABLE_VAL, \
                BIND_ENTITY_ID=FlowProperties.BIND_ENTITY_QUEUE, \
                ACKMODE=FlowProperties.ACKMODE_CLIENT, BIND_NAME=sys.argv[4])

rxMsg = 0
def rxFlowMsgCallback( session_p, msg_p, user_p ):
    global rxMsg
    rxMsg += 1
    print('Message received from flow.')
    return _defaultMsgCallback(session_p, msg_p, user_p)

funcInfo = FlowFuncInfo()
funcInfo.setMsgCallback(rxFlowMsgCallback)
funcInfo.setEventCallback(_defaultEventCallback)

flow = Flow(session, fprops, funcInfo)

import time
while rxMsg < 1:
    time.sleep(1)

session.disconnect()
