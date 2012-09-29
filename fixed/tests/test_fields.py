# Copyright (c) 2012 Simplistix Ltd
# See license.txt for license details.

from unittest import TestCase

from testfixtures import ShouldRaise, compare

from .. import Discriminator, Field, Skip, Constant, one_of

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

class TestConstants(TestCase):

    def test_attributes(self):
        c = Constant('X', "Execution")
        compare(c.text, 'X')
        compare(c.description, "Execution")

    def test_repr_str(self):
        c = Constant('X', "Execution")
        compare(repr(c), '<Execution>')
        compare(str(c), 'X')
    
    def test_equal(self):
        self.assertFalse(Constant('A', 'X')==Constant('A', 'Y'))
        
    def test_identity(self):
        self.assertFalse(Constant('A', 'X') is Constant('A', 'X'))

    def test_default_description(self):
        c = Constant('X')
        compare(c.text, 'X')
        compare(c.description, "X")
        compare(repr(c), '<X>')
        compare(str(c), 'X')

    def test_one_of_args(self):
        x = Constant('X')
        y = Constant('Y')
        convertor = one_of(x, y)
        self.assertTrue(convertor('X') is x)
        self.assertTrue(convertor('Y') is y)

    def test_one_of_kw(self):
        x = Constant('X')
        y = Constant('Y')
        convertor = one_of(x=x, y=y)
        self.assertTrue(convertor('X') is x)
        self.assertTrue(convertor('Y') is y)

    def test_one_of_duplicate_constant(self):
        with ShouldRaise(TypeError("Duplicate constant: 'X'")):
            one_of(Constant('X'), Constant('X'))

    def test_one_of_not_a_constant(self):
        with ShouldRaise(TypeError("Not a constant: 'X'")):
            one_of('X')
    
    def test_field(self):
        cx = Constant('X', 'foo')
        cy = Constant('Y', 'bar & baz (&_)')
        cz = Constant('Z')
        f = Field(1, one_of(cx, cy, z = cz))
        self.assertTrue(f.foo is cx)
        self.assertTrue(f.bar_baz is cy)
        self.assertTrue(f.z is cz)

    def test_field_overwrite_attr(self):
        with ShouldRaise(AttributeError("Constant cannot be stored as 'size'")):
            Field(1, one_of(Constant('S', 'size')))
        
    def test_field_overwrite_const_attr(self):
        with ShouldRaise(AttributeError("Constant cannot be stored as 'size'")):
            Field(1, one_of(Constant('S', 'size'), Constant('T', 'size')))
        
    def test_field_different_widths(self):
        with ShouldRaise(TypeError("<XX> does not have a size of 1")):
            Field(1, one_of(Constant('XX')))

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
