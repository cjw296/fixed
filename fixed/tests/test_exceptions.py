from unittest import TestCase

from .. import FixedException, UnknownRecordType, ConversionError, Problem

class TestUnknown(TestCase):

    def setUp(self):
        self.e = UnknownRecordType('X', 'XYZ')

    def test_subclassing(self):
        self.assertTrue(isinstance(self.e, FixedException))

    def test_attributes(self):
        self.assertEqual(self.e.discriminator, 'X')
        self.assertEqual(self.e.line, 'XYZ')

    def test_tuple(self):
        self.assertEqual(self.e[0], 'X')
        self.assertEqual(self.e[1], 'XYZ')
        self.assertEqual(len(self.e), 2)

    def test_repr(self):
        self.assertEqual(
            repr(self.e),
            "<UnknownRecordType discriminator='X', line='XYZ'>"
            )
    
class TestConversionError(TestCase):

    def setUp(self):
        self.e = ConversionError(dict(foo='x'), 'XYZ')

    def test_subclassing(self):
        self.assertTrue(isinstance(self.e, FixedException))

    def test_attributes(self):
        self.assertEqual(self.e.problems, dict(foo='x'))
        self.assertEqual(self.e.line, 'XYZ')

    def test_tuple(self):
        self.assertEqual(self.e[0], dict(foo='x'))
        self.assertEqual(self.e[1], 'XYZ')
        self.assertEqual(len(self.e), 2)

    def test_repr(self):
        self.assertEqual(
            repr(self.e),
            "<ConversionError problems={'foo': 'x'}, line='XYZ'>"
            )
    
class TestProblem(TestCase):

    def setUp(self):
        self.p = Problem('X', int, TypeError('Foo'))
        
    def test_str(self):
        self.assertEqual(
            str(self.p),
            "Could not convert 'X' using <type 'int'>, gave TypeError('Foo',)"
            )
        
    def test_repr(self):
        self.assertEqual(
            repr(self.p),
            "<Problem: Could not convert 'X' using <type 'int'>, gave TypeError('Foo',)>"
            )
