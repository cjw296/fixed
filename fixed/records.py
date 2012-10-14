# Copyright (c) 2012 Simplistix Ltd
# See license.txt for license details.

from collections import namedtuple
from operator import attrgetter

from exceptions import Problem, ConversionError
from fields import Discriminator, Ordered, Skip

class RecordMeta(type):

    def __init__(cls, class_name, bases, elements):
        if bases==(object,):
            return
        
        specs = []
        for name, obj in elements.items():
            if isinstance(obj, Ordered):
                obj.name = name
                specs.append(obj)
        specs.sort(key=attrgetter('order'))

        index = 0
        discriminator = []
        type_fields = []
        cls.fields = []
        
        for obj in specs:
            if isinstance(obj, Skip):
                index += obj.size
            else:
                if obj.start is not None:
                    index = obj.start
                next_index = index + obj.size
                type_fields.append(obj.name)
                s = slice(index, next_index)
                cls.fields.append((s, obj.convertor))

                if isinstance(obj, Discriminator):
                    obj.slice = s
                    discriminator.append(obj)
                    
                index = next_index

        if len(discriminator)>1:
            raise TypeError(
                'Multiple discriminators are not supported, found: %r' % (
                    [d.name for d in discriminator]
                    ))
        if not discriminator:
            raise TypeError('No discriminator specified')
        cls.disc = discriminator[0]
        cls.type = namedtuple(class_name+'Type', type_fields)

class Record(object):
    
    __metaclass__ = RecordMeta

    def __new__(self, line):
        # fast
        return self.type(*(
            line[s] if convert is None else convert(line[s])
            for s, convert in self.fields
            ))

    @classmethod
    def explain(cls, line):
        # safe and verbose, but slow
        problems = {}
        elements = []
        for name, field in zip(cls.type._fields, cls.fields):
            s, convert = field
            raw = line[s]
            try:
                value = (convert or str)(line[s])
            except Exception, e:
                problems[name] = Problem(raw, convert, e)
            else:
                elements.append(value)
        if problems:
            return ConversionError(problems, line)
        return cls.type(*elements)
