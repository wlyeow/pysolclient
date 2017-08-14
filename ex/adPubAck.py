#!/usr/bin/env python3

from pysolclient import *
from pysolclient import _defaultMsgCallback
import common
import sys
import time
import collections as co

class AckTracker:
    def __init__(self, msg):
        self.msg = msg #retain msg ref for eventCallback
        self.acked = False
        self.accepted = False

def eventCallback(session_p, eventInfo_p, user_p):
    event = eventInfo_p.contents.sessionEvent
    corr_p  = eventInfo_p.contents.correlation_p

    if event == SessionEvent.ACKNOWLEDGEMENT:
        LOG.log(LOG.INFO, 'eventCallback - {}'.format(
                SessionEvent.toString(event)))

        acker = common.CallbackObject.deref(corr_p)
        print('Acknowledged Seq {}'.format(acker.msg.getSeqNum()))
        # remove circular ref
        del acker.msg
        acker.accepted = True
        acker.acked = True
        return

    if event == SessionEvent.REJECTED_MSG_ERROR:
        info_p = getLastErrorInfo()
        LOG.log(LOG.ERROR,
                'eventCallback - {}; subCode {}, responseCode {}, reason {}'.format(
                    SessionEvent.toString(event),
                    SubCode.toString( info_p.contents.subCode ),
                    info_p.contents.responseCode,
                    info_p.contents.errorStr.decode()) )

        acker = common.CallbackObject.deref(corr_p)
        print('Rejected Seq {}'.format(acker.msg.getSeqNum()))
        # remove circular ref
        del acker.msg
        acker.accepted = False
        acker.acked = True
        return

    if event == SessionEvent.UP_NOTICE or \
        event == SessionEvent.TE_UNSUBSCRIBE_OK or \
        event == SessionEvent.CAN_SEND or \
        event == SessionEvent.RECONNECTING_NOTICE or \
        event == SessionEvent.RECONNECTED_NOTICE or \
        event == SessionEvent.PROVISION_OK or \
        event == SessionEvent.SUBSCRIPTION_OK:

            LOG.log(LOG.INFO, 'eventCallback - {}\n'.format(
                SessionEvent.toString(event)))

    elif event == SessionEvent.DOWN_ERROR or \
        event == SessionEvent.CONNECT_FAILED_ERROR or \
        event == SessionEvent.SUBSCRIPTION_ERROR or \
        event == SessionEvent.RX_MSG_TOO_BIG_ERROR or \
        event == SessionEvent.TE_UNSUBSCRIBE_ERROR or \
        event == SessionEvent.PROVISION_ERROR:

            info_p = getLastErrorInfo()
            
            LOG.log(LOG.ERROR,
                    'eventCallback - {}; subCode {}, responseCode {}, reason {}\n'.format(
                        SessionEvent.toString(event),
                        SubCode.toString( info_p.contents.subCode ),
                        info_p.contents.responseCode,
                        info_p.contents.errorStr.decode()) )
    
    else:
        LOG.log(LOG.ERROR,
                'eventCallback - {}; Unrecognized or deprecated event.\n'.format(
                    SessionEvent.toString(event)))

def main_run():
    conf = common.init('n', (True, *'tq'))
    
    context = Context()
    sprops = SessionProperties(HOST=conf.host, VPN_NAME=conf.user.vpn, USERNAME=conf.user.name, GENERATE_SEQUENCE_NUMBER="1")
    
    def rxMsgCallback(session_p, msg_p, user_p):
        return CALLBACK_OK
    
    funcInfo = SessionFuncInfo()
    funcInfo.setMsgCallback(rxMsgCallback, None)
    funcInfo.setEventCallback(eventCallback)
    
    session = Session(context, sprops, funcInfo)
    session.connect()
    
    dest = None
    if conf.topic:
        print('Publish to topic {}.'.format(conf.topic))
        dest = Destination(conf.topic)
    elif conf.queue:
        print('Publish to queue {}.'.format(conf.queue))
        dest = Destination(conf.queue, Destination.QUEUE)
    else:
        raise RuntimeError('Invalid topic or queue')
    
    atqueue = co.deque()
    while conf.num > 0:
        msg = Message()
        at = AckTracker(msg)
        atqueue.append(at)

        err = msg.applyProps( \
                Dest=dest,
                BinaryAttachment='Hello World!\n'.encode(),
                Delivery=Message.DELIVERY_MODE_PERSISTENT,
                CorrTag=common.CallbackObject.wrap(at))

        if err:
            for n, e in err.items():
                print('Cannot set {}:\t{}: {}'.format(n, type(e).__name__, str(e)))
            raise RuntimeError('Cannot continue')

        session.sendMsg(msg)
        conf.num -= 1
        print('Message sent, {} to go'.format(conf.num))
    
    print('Waiting for acks')
    numAcked = 0
    numAccepted = 0
    while len(atqueue) > 0:
        if atqueue[0].acked:
            numAcked += 1
            if atqueue[0].accepted:
                numAccepted += 1
            atqueue.pop()
    
    time.sleep(0.1)
    session.disconnect()

    print('{} acked, {} accepted'.format(numAcked, numAccepted))

if __name__ == '__main__':
    main_run()
