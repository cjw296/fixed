# Copyright (c) 2012 Simplistix Ltd
# See license.txt for license details.

from collections import namedtuple
from operator import attrgetter

import re

# field types

class Ordered(object):
    order = 0
    def __new__(cls, *args, **kw):
        obj = object.__new__(cls, *args, **kw)
        obj.order = Ordered.order
        Ordered.order += 1
        return obj
        
class Field(Ordered):
    def __init__(self, size, convertor=None, start=None):
        self.size = size
        self.convertor = convertor
        self.start = start
        if isinstance(convertor, one_of):
            for attr, const in convertor.attrs.items():
                if attr in self.__dict__:
                    raise AttributeError('Constant cannot be stored as %r' % attr)
                if len(const.text) != self.size:
                    raise TypeError('%r does not have a size of %i' % (
                        const, self.size
                        ))
                setattr(self, attr, const)
                

class Discriminator(Field):
    slice = slice(None, None)
    def __init__(self, text, *args, **kw):
        super(Discriminator, self).__init__(len(text), *args, **kw)
        self.text = text
    def __repr__(self):
        return '<Discriminator %r (%s-%s)>' % (
            self.text, self.slice.start, self.slice.stop
            )

class Skip(Ordered):
    def __init__(self, size):
        self.size = size

# constants

class Constant(object):
    def __init__(self, text, description=None):
        self.text = text
        self.description = description or text
    def __repr__(self):
        return '<%s>' % self.description
    def __str__(self):
        return self.text

_attr_re = re.compile('\W+')

class one_of(dict):
    
    def __init__(self, *consts, **kw):
        self.attrs = {}
        for const in consts:
            if not isinstance(const, Constant):
                raise TypeError('Not a constant: %r' % const)
            self[const.text] = const
            attr = _attr_re.sub('_', const.description).strip('_')
            self.attrs[attr] = const
        for attr, const in kw.items():
            self[const.text] = const
            self.attrs[attr] = const

    def __setitem__(self, text, value):
        if text in self:
            raise TypeError('Duplicate constant: %r' % text)
        super(one_of, self).__setitem__(text, value)
        
    def __call__(self, text):
        return self[text]

# record type

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

class Problem(object):

    def __init__(self, raw, convert, exception):
        self.raw, self.convert, self.exception = (
            raw, convert, exception
            )
    def __str__(self):
        return 'Could not convert %r using %r, gave %r' % (
            self.raw, self.convert, self.exception
            )
    def __repr__(self):
        return '<Problem: %s>' % self

# exceptions
class FixedException(Exception):

    __slots__ = ()
    
    def __len__(self):
        return len(self.__slots__)
    
    def __getitem__(self, index):
        return getattr(self, self.__slots__[index])

    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            ', '.join(
                ['%s=%r' % (name, getattr(self, name))
                 for name in self.__slots__]
                ))
            
class UnknownRecordType(FixedException):
    __slots__ = ('discriminator', 'line')
    def __init__(self, discriminator, line):
        self.discriminator, self.line = discriminator, line
      

class ConversionError(FixedException):
    __slots__ = ('problems', 'line')
    def __init__(self, problems, line):
        self.problems, self.line = problems, line


    
