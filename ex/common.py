import argparse as ap
import pysolclient as solclient

class MetaParser(type):
    def __init__(cls, name, bases, d):
        type.__init__(cls, name, bases, d)
        cls._opts = { \
                'c' : { 'dest': 'host', 'required': True, 'help': '[{tcp|tcps|ws|wss}://][ ip | host ][:port]' },
                'u' : { 'dest': 'user', 'default': 'default@default', 'type': cls.User, 'help': '[username][@vpn]' },
                'l' : { 'dest': 'log', 'metavar': 'LEVEL', 'help': 'log level' },
                't' : { 'dest': 'topic', 'default': 'my/sample/topic', 'help': 'smf/topic/name' },
                'q' : { 'dest': 'queue', 'default': 'my_sample_queue', 'help': 'durable/queue/name' },
                'e' : { 'dest': 'tpe', 'metavar': 'TOPIC-ENDPOINT', 'default': 'my_sample_topicendpoint', 'help': 'durable/topic/endpoint/name' },
            }

class Parser(metaclass=MetaParser):
    
    class User:
        def __init__(self, param):
            tmp = param.split('@')
            self.name = tmp[0]
            if len(tmp) > 1:
                self.vpn = tmp[1]
            else:
                self.vpn = 'default'
    
        def __repr__(self):
            return self.name + '@' + self.vpn

    def __init__(self, *args):
        self.parser = ap.ArgumentParser(conflict_handler='resolve')
        if args is not None: self.add(*args)

    def add(self, *args):
        for arg in args:
            if arg in self._opts:
                self.parser.add_argument('-'+arg, **(self._opts[arg]))

    def hide(self, *args):
        new_parser = ap.ArgumentParser(parents=[self.parser], conflict_handler='resolve')
        for arg in args:
            if isinstance(arg, str): new_parser.add_argument('-'+arg, help=ap.SUPPRESS)
        self.parser = new_parser

    def parse(self):
        args = self.parser.parse_args()
        return args


def init(opts):
    p = Parser(*('cu'+opts+'l'))
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


if __name__ == "__main__":
    args = init('tqe')
    print(args)

