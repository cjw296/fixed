# Copyright (c) 2012 Simplistix Ltd
# See license.txt for license details.

from unittest import TestCase

from testfixtures import ShouldRaise, compare

from .. import Discriminator, Record, Field, Discriminator, Skip

class TestRecord(TestCase):

    def test_normal(self):

        d = Discriminator('N')
        class Normal(Record):
            id = d
            data  = Field(2, int)
        
        self.assertTrue(Normal.disc is d)
        compare(d.slice, slice(0, 1))
                
        tuple_type = Normal.type
        self.assertTrue(issubclass(tuple_type, tuple))
        compare(tuple_type.__name__, 'NormalRecord')

        compare(Normal.id.name, 'id')
        compare(Normal.data.name, 'data')
        
        result = Normal('N 2')
        compare(tuple_type(id='N', data=2), result, strict=True)
        
    def test_discriminator_not_first(self):

        # we have to do both out here to get them created in the right order
        f = Field(2, int)
        d = Discriminator('N')
        
        class Normal(Record):
            data = f
            id = d
            
        self.assertTrue(Normal.disc is d)
        compare(d.slice, slice(2, 3))
        
        tuple_type = Normal.type
        self.assertTrue(issubclass(tuple_type, tuple))
        compare(tuple_type.__name__, 'NormalRecord')

        compare(Normal.id.name, 'id')
        compare(Normal.data.name, 'data')
        
        result = Normal('2 N')
        compare(tuple_type(id='N', data=2), result, strict=True)
        
    def test_sparse_skip(self):

        # we have to do both out here to get them created in the right order
        s = Skip(1)
        d = Discriminator('N')
        
        class Normal(Record):
            junk = s
            id = d
            unused = Skip(2)
            data  = Field(1, int)
        
        self.assertTrue(Normal.disc is d)
        compare(d.slice, slice(1, 2))
                
        tuple_type = Normal.type
        self.assertTrue(issubclass(tuple_type, tuple))
        compare(tuple_type.__name__, 'NormalRecord')

        compare(Normal.junk.name, 'junk')
        compare(Normal.id.name, 'id')
        compare(Normal.unused.name, 'unused')
        compare(Normal.data.name, 'data')
        
        result = Normal('XNXX2')
        compare(tuple_type(id='N', data=2), result, strict=True)

    def test_sparse_indexes(self):

        d = Discriminator('N', start=1)
        class Normal(Record):
            id = d
            data  = Field(1, int, start=4)
        
        self.assertTrue(Normal.disc is d)
        compare(d.slice, slice(1, 2))
                
        tuple_type = Normal.type
        self.assertTrue(issubclass(tuple_type, tuple))
        compare(tuple_type.__name__, 'NormalRecord')

        compare(Normal.id.name, 'id')
        compare(Normal.data.name, 'data')
        
        result = Normal('XNXX2')
        compare(tuple_type(id='N', data=2), result, strict=True)

    def test_multiple_discriminator(self):

        with ShouldRaise(TypeError(
            "Multiple discriminators are not supported, found: ['d1', 'd2']"
            )):
            class Normal(Record):
                d1 = Discriminator('N')
                d2 = Discriminator('M')

    def test_no_discriminator(self):
        with ShouldRaise(TypeError('No discriminator specified')):
            class Normal(Record):
                pass
