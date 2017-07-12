from pysolclient import *
from ctypes import *
import inspect

class TestMessageClass:
    @classmethod
    def setup_class(cls):
        cls.msg = Message()

    @classmethod
    def teardown_class(cls):
        del cls.msg

    def test_binary_attachment(self):
        filename = inspect.getfile(inspect.currentframe())
        contents = None
        with open(filename, 'rb') as f:
            contents = f.read()
            self.msg.setBinaryAttachment(contents)

        attached = self.msg.getBinaryAttachment()
        
        print('len(f) = {}, len(m) = {}'.format(len(contents), len(attached)))

        assert contents == attached

    def test_no_binary_attachment(self):
        self.msg.setBinaryAttachment(None)
        assert self.msg.getBinaryAttachment() is None

    def test_TTL(self):
        outofrange = False
        try:
            self.msg.setTTL(9223372036854775807) # max int64
        except SolaceError:
            outofrange = True
        assert outofrange

        outofrange = False
        try:
            self.msg.setTTL(-1000)
        except SolaceError:
            outofrange = True
        assert outofrange

        ttl = 214748364700 # max int32 * 100
        self.msg.setTTL(ttl)
        assert ttl == self.msg.getTTL()

    def test_AppMsgId(self):
        id = 'x'
        for _ in range(20):
            id += id

        self.msg.setAppMsgId(id)
        assert id == self.msg.getAppMsgId()

    def test_SeqNum(self):
        seq = 9223372036854775807 # max int64
        self.msg.setSeqNum(seq)
        assert seq == self.msg.getSeqNum()

    def test_COS(self):
        self.msg.setCOS(Message.COS_3)
        assert Message.COS_3 == self.msg.getCOS()

    def test_DMQ(self):
        self.msg.setDMQ(True)
        assert self.msg.isDMQ()
        
        self.msg.setDMQ(False)
        assert self.msg.isDMQ() == False

    def test_DTO(self):
        self.msg.setDTO(True)
        assert self.msg.isDTO()
        
        self.msg.setDTO(False)
        assert self.msg.isDTO() == False

    def test_Eliding(self):
        self.msg.setEliding(True)
        assert self.msg.isEliding()
        
        self.msg.setEliding(False)
        assert self.msg.isEliding() == False

    def test_Destination(self):
        d = Destination('some/topic/string')
        self.msg.setDest(d)
        assert self.msg.getDest() == d
