# Copyright (c) 2012 Simplistix Ltd
# See license.txt for license details.

from constants import one_of

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
                if (len(const.text) != self.size) and convertor.size_check:
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
