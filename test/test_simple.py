from pysolclient import *
from pysolclient import _defaultEventCallback
from ctypes import *
import time
import pprint

def test_destination_eq():
    c = Destination()
    d = Destination()

    c.setDest('c')
    d.setDest('d')
    assert c != d

    d.setDest('c')
    assert c == d

    c.destType = Destination.QUEUE
    assert c != d

    d.destType = Destination.QUEUE
    assert c == d

def test_connect_non_blocking():
    context = Context()

    sprops = SessionProperties(\
            HOST='localhost',
            VPN_NAME='default',
            USERNAME='default',
            CONNECT_BLOCKING=PROP_DISABLE_VAL)

    session = Session(context, sprops)
    
    assert session.connect() == ReturnCode.IN_PROGRESS

class TestDirectMessages:
    @classmethod
    def setup_class(cls):
        cls.context = Context()

    @classmethod
    def teardown_class(cls):
        del cls.context

    def setup(self):
        self.sprops = SessionProperties(\
                HOST='localhost',
                VPN_NAME='default',
                USERNAME='default')


    class SeqNumData:
        def __init__(self):
            self.last = None
            self.noSeqNum = 0
            self.missing = []
            self.discard = []
            self.received = 0

    def test_sequence_numbers(self):
        self.sprops.GENERATE_SEQUENCE_NUMBER = PROP_ENABLE_VAL
        topic = 'nosetest/direct/test_seq_num'
        messages = 10000
        wait_timeout = 10

        # setup rx
        def rxMsg(session_p, msg_p, user_p):
            udata = cast(user_p, POINTER(py_object)).contents.value
            udata.received += 1

            msg = Message(msg_p)

            m = msg.getSeqNum()
            if m is None:
                udata.noSeqNum += 1
                return CALLBACK_TAKE_MSG

            if msg.isDiscardIndicated():
                udata.discard.append(m)

            if udata.last is None:
                udata.last = m
                return CALLBACK_TAKE_MSG

            if udata.last + 1 != m:
                udata.missing.extend(range(udata.last + 1, m))

            udata.last = m

            return CALLBACK_TAKE_MSG

        # setup funcInfo
        data = self.SeqNumData()
        D = py_object(data)
        funcInfo = SessionFuncInfo()
        funcInfo.rxMsgInfo.callback_p = MSG_CALLBACK_TYPE(rxMsg)
        funcInfo.rxMsgInfo.user_p = cast(byref(D), c_void_p)
        funcInfo.eventInfo.callback_p = EVENT_CALLBACK_TYPE(_defaultEventCallback)

        session = Session(self.context, self.sprops, funcInfo)
        session.connect()
        
        session.topicSubscribe(topic)

        msg = Message()
        err = msg.applyProps(Dest=Destination(topic),
                Delivery=Message.DELIVERY_MODE_DIRECT)
        if err:
            for n, e in err.items():
                print('Cannot set {}:\t{}: {}'.format(n, type(e).__name__, str(e)))
                if e.trace: print(e.trace)
            raise RuntimeError('Cannot continue')

        for _ in range(messages):
            session.sendMsg(msg)

        while wait_timeout > 0:
            if data.received == messages: break
            time.sleep(0.1)
            wait_timeout -= 0.1

        session.disconnect()

        pprint.pprint(data.__dict__)

        assert data.received == messages
