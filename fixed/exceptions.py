# Copyright (c) 2012 Simplistix Ltd
# See license.txt for license details.

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

    def __str__(self):
        return ', '.join(
                ['%s=%r' % (name, getattr(self, name))
                 for name in self.__slots__]
                )
    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            str(self),
            )
            
class UnknownRecordType(FixedException):
    __slots__ = ('discriminator', 'line')
    def __init__(self, discriminator, line):
        self.discriminator, self.line = discriminator, line
      

class ConversionError(FixedException):
    __slots__ = ('problems', 'line')
    def __init__(self, problems, line):
        self.problems, self.line = problems, line


