import argparse as ap
import pysolclient as solclient
from ctypes import *

class MetaParser(type):
    def __init__(cls, name, bases, d):
        type.__init__(cls, name, bases, d)
        cls._opts = { \
                'c' : { 'dest': 'host', 'required': True, 'help': '[{tcp|tcps|ws|wss}://][ ip | host ][:port]' },
                'u' : { 'dest': 'user', 'default': 'default@default', 'type': cls.User, 'help': '[username][@vpn]' },
                'p' : { 'dest': 'passwd', 'help': '[passwd]' },
                'l' : { 'dest': 'log', 'metavar': 'LEVEL', 'help': 'log level' },
                't' : { 'dest': 'topic', 'nargs': '?', 'const': 'my/sample/topic', 'help': 'smf/topic/name' },
                'q' : { 'dest': 'queue', 'nargs': '?', 'const': 'my_sample_queue', 'help': 'durable/queue/name' },
                'e' : { 'dest': 'tpe', 'metavar': 'TOPIC-ENDPOINT', 'nargs': '?', 'const': 'my_sample_topicendpoint', 'help': 'durable/topic/endpoint/name' },
                'n' : { 'dest': 'num', 'default': 10, 'type': int, 'help': 'number of messages' },
            }

class Parser(metaclass=MetaParser):
    
    class User:
        def __init__(self, param):
            tmp = param.split('@')
            self.name = tmp[0] if tmp[0] != '' else 'default'
            if len(tmp) > 1:
                self.vpn = tmp[1]
            else:
                self.vpn = 'default'
    
        def __repr__(self):
            return self.name + '@' + self.vpn

    def __init__(self, *args):
        self.parser = ap.ArgumentParser(conflict_handler='resolve')
        if args is not None: self.add(*args)

    def add(self, *args, parser=None):
        if parser is None:
            parser = self.parser
        for arg in args:
            if type(arg) is tuple:
                g = parser.add_mutually_exclusive_group(required=arg[0])
                self.add(*arg[1:], parser=g)
            elif type(arg) is list:
                g = parser.add_argument_group(title=arg[0])
                self.add(*arg[1:], parser=g)
            elif arg in self._opts:
                parser.add_argument('-'+arg, **(self._opts[arg]))

    def hide(self, *args):
        new_parser = ap.ArgumentParser(parents=[self.parser], conflict_handler='resolve')
        for arg in args:
            if isinstance(arg, str): new_parser.add_argument('-'+arg, help=ap.SUPPRESS)
        self.parser = new_parser

    def parse(self):
        args = self.parser.parse_args()
        return args

def init(*opts):
    p = Parser(*(list('cu')+list(opts)+['l']))
    args = p.parse()

    if args.log is not None:
        if args.log == 'debug':
            solclient.LOG.setFilterLevel(solclient.LOG.CATEGORY_ALL, solclient.LOG.DEBUG)
        elif args.log == 'info':
            solclient.LOG.setFilterLevel(solclient.LOG.CATEGORY_ALL, solclient.LOG.INFO)
        elif args.log == 'notice':
            solclient.LOG.setFilterLevel(solclient.LOG.CATEGORY_ALL, solclient.LOG.NOTICE)
        elif args.log == 'warn':
            solclient.LOG.setFilterLevel(solclient.LOG.CATEGORY_ALL, solclient.LOG.WARNING)
        elif args.log == 'error':
            solclient.LOG.setFilterLevel(solclient.LOG.CATEGORY_ALL, solclient.LOG.ERROR)
        elif args.log == 'crit':
            solclient.LOG.setFilterLevel(solclient.LOG.CATEGORY_ALL, solclient.LOG.CRITICALL)
        elif args.log == 'alert':
            solclient.LOG.setFilterLevel(solclient.LOG.CATEGORY_ALL, solclient.LOG.ALERT)
        elif args.log == 'emerg':
            solclient.LOG.setFilterLevel(solclient.LOG.CATEGORY_ALL, solclient.LOG.EMERGENCY)

    return args

class CType:
    @classmethod
    def wrapObj(cls, o, t=py_object):
        return t(o)

    @classmethod
    def derefObj(cls, o, t=py_object):
        return cast(o, POINTER(t)).contents.value

    def __init__(self, t):
        if callable(t) and type(t).__module__ == '_ctypes':
            self.ctype = t
        else:
            raise TypeError('not a ctype callable')

    def wrap(self, o):
        return self.wrapObj(o, self.ctype)

    def deref(self, o):
        return self.derefObj(o, self.ctype)

cbObject = CType(py_object)
cbString = CType(c_char_p)

if __name__ == "__main__":
    args = init('tqe')
    print(args)
