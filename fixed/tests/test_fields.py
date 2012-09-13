# Copyright (c) 2012 Simplistix Ltd
# See license.txt for license details.

from unittest import TestCase

from testfixtures import compare

from .. import Discriminator, Field, Skip

class TestField(TestCase):

    def test_default_attributes(self):
        f = Field(1)
        compare(f.size, 1)
        compare(f.convertor, None)
        compare(f.start, None)
        self.assertTrue(isinstance(f.order, int))
            
    def test_specified_attributes(self):
        def conv(txt): pass
        f = Field(1, conv, 2)
        compare(f.size, 1)
        compare(f.convertor, conv)
        compare(f.start, 2)
        self.assertTrue(isinstance(f.order, int))
        
    def test_order(self):
        f1 = Field(1)
        f2 = Field(2)
        self.assertTrue(f1.order < f2.order)

class TestDiscriminator(TestCase):

    def test_default_attributes(self):
        d = Discriminator('FOO')
        compare(d.size, 3)
        compare(d.convertor, None)
        compare(d.start, None)
        compare(d.text, 'FOO')
        self.assertTrue(isinstance(d.order, int))
        
    def test_specified_attributes(self):
        def conv(txt): pass
        d = Discriminator('FOO', conv, 2)
        compare(d.size, 3)
        compare(d.convertor, conv)
        compare(d.start, 2)
        compare(d.text, 'FOO')
        self.assertTrue(isinstance(d.order, int))
        
    def test_order(self):
        f = Field(1)
        d = Discriminator('FOO')
        self.assertTrue(f.order < d.order)

class TestSkip(TestCase):

    def test_attributes(self):
        s = Skip(4)
        compare(s.size, 4)
        self.assertTrue(isinstance(s.order, int))
        
    def test_order(self):
        f = Field(1)
        s = Skip(4)
        self.assertTrue(f.order < s.order)
