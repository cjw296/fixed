# Copyright (c) 2012 Simplistix Ltd
# See license.txt for license details.

import re

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

    size_check = True
    
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

def all(field):
    if not isinstance(field.convertor, one_of):
        raise TypeError(
            'convertor is %r, not a one_of instance' % field.convertor
            )
    result = []
    for _, constant in sorted(field.convertor.items()):
        result.append(constant)
    return result
