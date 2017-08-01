#!/usr/bin/env python3

from pysolclient import *
from pysolclient import _defaultMsgCallback
from pysolclient import _defaultEventCallback
import sys

def main():
    context = Context()
    sprops = SessionProperties(HOST=sys.argv[1], VPN_NAME=sys.argv[2], USERNAME=sys.argv[3])
    
    session = Session(context, sprops)
    session.connect()
    
    epprops = EndpointProperties(ID=EndpointProperties.QUEUE, \
            NAME=sys.argv[4], PERMISSION=EndpointProperties.PERM_CONSUME)
    
    print('Provisioning endpoint {}.'.format(sys.argv[4]))
    session.epProvision(epprops, ProvisionFlags.IGNORE_EXIST_ERRORS | ProvisionFlags.WAITFORCONFIRM)
    
    fprops = FlowProperties(BIND_BLOCKING=PROP_ENABLE_VAL, \
                    BIND_ENTITY_ID=FlowProperties.BIND_ENTITY_QUEUE, \
                    ACKMODE=FlowProperties.ACKMODE_CLIENT, BIND_NAME=sys.argv[4])
    
    rxMsg = c_int(0)
    def rxFlowMsgCallback( flow_p, msg_p, user_p ):
        cast(user_p, POINTER(c_int)).contents.value += 1
        print('Message received from flow.')

        _defaultMsgCallback(None, msg_p, None)
        Flow.ack(flow_p, msg_p)

        return CALLBACK_OK
    
    funcInfo = FlowFuncInfo()
    funcInfo.setMsgCallback(rxFlowMsgCallback, byref(rxMsg))
    funcInfo.setEventCallback(_defaultEventCallback)
    
    flow = Flow(session, fprops, funcInfo)
    
    import time
    while rxMsg.value < 1:
        time.sleep(1)
    
    del flow
    session.disconnect()

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('Usage: {} <ip> <vpn> <username> <queue>'.format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)
    
    LOG.setFilterLevel(LOG.CATEGORY_APP, LOG.INFO)
    main()
