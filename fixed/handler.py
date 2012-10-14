# Copyright (c) 2012 Simplistix Ltd
# See license.txt for license details.

from exceptions import FixedException

class HandlerMeta(type):
    
    def __new__(cls, class_name, bases, dict_):
        dict_['handlers'] = handlers = {}
        dict_['parse_only'] = parse_only = []
        discs = {}
        for name, obj in dict_.items():
            handles = getattr(obj, '__handles__', ())
            for thing in handles:
                if isinstance(thing, type) and issubclass(thing, FixedException):
                    handlers[thing] = obj
                else:
                    handlers[thing.type] = obj
                    dict_['parser'] = thing._parser
                    parse_only.append(thing)
        return type.__new__(cls, class_name, bases, dict_)

class Handler(object):

    __metaclass__ = HandlerMeta

    parse_unknown = True
    
    def handle(self, iterable):
        for record in self.handled(iterable):
            pass
              
    def handled(self, iterable):
        for i, record in enumerate(self.parser(
            iterable, self.parse_only, self.parse_unknown
            )):
            handler = self.handlers.get(record.__class__)
            if handler is not None:
                yield handler(self, iterable, i+1, record)
            elif isinstance(record, Exception):
                raise record

class handles(object):
    def __init__(self, type):
        self.type = type
    def __call__(self, method):
        if getattr(method, '__handles__', None) is None:
            method.__handles__ = []
        method.__handles__.append(self.type)
        return method
    
    
