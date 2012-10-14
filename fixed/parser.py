# Copyright (c) 2012 Simplistix Ltd
# See license.txt for license details.

from collections import namedtuple
from operator import attrgetter

from exceptions import UnknownRecordType
from records import Record

class ParserMeta(type):

    def __new__(cls, class_name, bases, dict_):
        dict_['record_mapping'] = record_mapping = {}
        discs = {}
        records = []
        for name, obj in dict_.items():
            if isinstance(obj, type) and issubclass(obj, Record):
                disc = obj.disc
                discs[disc.slice.start, disc.slice.stop] = disc
                records.append(obj)
                record_mapping[disc.text] = obj
        discs = discs.values()
        if len(discs)>1:
            raise TypeError('Inconsistent discriminators: %r' % discs)
        if discs:
            dict_['disc_slice'] = discs[0].slice
        parser = type.__new__(cls, class_name, bases, dict_)
        for record in records:
            record._parser = parser
        return parser

ignore = object()

class Parser(object):

    __metaclass__ = ParserMeta
    
    def __init__(self, iterable, parse_only=None, parse_unknown=True):
        self.iterable = iterable
        self.parse_unknown = parse_unknown
        if parse_only:
            record_mapping = {}
            for k, type in self.record_mapping.items():
                if type in parse_only:
                    t = type
                else:
                    t = ignore
                record_mapping[k] = t
            self.record_mapping = record_mapping

    def __iter__(self):
        # NB: this will always return an object for each record in the
        #     file, so enumerate can reliably be used to figure out
        #     line numbers if needed
        for row in self.iterable:
            disc = row[self.disc_slice]
            record_type = self.record_mapping.get(disc)
            if record_type is None:
                if self.parse_unknown:
                    yield UnknownRecordType(disc, row)
                continue
            elif record_type is ignore:
                continue
            try:
                yield record_type(row)
            except Exception:
                yield record_type.explain(row)
