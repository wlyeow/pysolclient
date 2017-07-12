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
        ttl = 9223372036854775807 # max int64
        outofrange = False
        try:
            self.msg.setTTL(ttl)
        except SolaceError:
            outofrange = True
        assert outofrange

        outofrange = False
        ttl = -1000
        try:
            self.msg.setTTL(ttl)
        except SolaceError:
            outofrange = True
        assert outofrange

        ttl = 214748364700 # max int32 * 100
        self.msg.setTTL(ttl)
        gttl = self.msg.getTTL()

        assert gttl == ttl

    def test_AppMsgId(self):
        id = 'x'
        for _ in range(20):
            id += id

        self.msg.setAppMsgId(id)
        gid = self.msg.getAppMsgId()

        print(gid)

        assert id == gid

    def test_SeqNum(self):
        seq = 9223372036854775807 # max int64
        self.msg.setSeqNum(seq)
        gseq = self.msg.getSeqNum()

        assert seq == gseq

    def test_COS(self):
        self.msg.setCOS(Message.COS_3)
        assert Message.COS_3 == self.msg.getCOS()
