# Copyright (c) 2012 Simplistix Ltd
# See license.txt for license details.

from unittest import TestCase

from testfixtures import (
    Comparison as C,
    ShouldRaise,
    TempDirectory,
    compare,
    generator,
    )

from .. import (
    Chunker,
    Constant,
    Discriminator,
    Field,
    Parser,
    Record,
    Skip,
    UnknownRecordType,
    ConversionError,
    one_of,
    )

class TestParser(TestCase):

    def setUp(self):
        class TheParser(Parser):
            class ARecord(Record):
                prefix = Discriminator('A')
                data = Field(2)
            class BRecord(Record):
                prefix = Discriminator('B')
                data = Field(2)
        self.parser = TheParser
        
    def test_simple(self):
        # we use our own parser to get a convertor and a constant in there
        class TheParser(Parser):
            
            class ARecord(Record):
                prefix = Discriminator('A')
                data = Field(2, int)
                const = Field(1, one_of(
                    x = Constant('X', 'an X'),
                    y = Constant('Y', 'a Y'),
                    ))
                    
            class BRecord(Record):
                prefix = Discriminator('B')
                d1 = Field(2)
                d2 = Field(2)

        compare(generator(
            TheParser.BRecord.type(prefix='B', d1='XX', d2='YY'),
            TheParser.ARecord.type(prefix='A',
                                   data=2,
                                   const=TheParser.ARecord.const.x
                                   ),
            TheParser.ARecord.type(prefix='A',
                                   data=13,
                                   const=TheParser.ARecord.const.y),
            ), TheParser(['BXXYY', 'A 2X', 'A13Y']))
            

    def test_file(self):
        with TempDirectory() as dir:
            path = dir.write('file', 'AXX\nBYY\n')
            with open(path) as source:
                compare(generator(
                    self.parser.ARecord.type('A', 'XX'),
                    self.parser.BRecord.type('B', 'YY'),
                    ), self.parser(source))
                
    def test_parse_only(self):
        compare(generator(
            self.parser.ARecord.type('A', 'XX'),
            ), self.parser(['AXX', 'BXX'], parse_only=[self.parser.ARecord]))

    def test_fixed_width(self):
        # make sure file wrapped with iterator works
        with TempDirectory() as dir:
            path = dir.write('file', 'AXXBYY')
            with open(path) as source:
                compare(generator(
                    self.parser.ARecord.type('A', 'XX'),
                    self.parser.BRecord.type('B', 'YY'),
                    ), self.parser(Chunker(source, 3)))
    
    def test_type_identity(self):
        record = iter(self.parser(['AXX'])).next()

        self.assertTrue(isinstance(record, self.parser.ARecord.type))
        self.assertTrue(type(record) == self.parser.ARecord.type)
        self.assertFalse(isinstance(record, self.parser.ARecord)) # :-(
        
        
    def test_const_equality_identity(self):
        class TheParser(Parser):
            class ARecord(Record):
                prefix = Discriminator('A')
                const = Field(1, one_of(
                    x = Constant('X', 'an X'),
                    y = Constant('Y', 'a Y'),
                    ))
                
        record = iter(TheParser(['AX'])).next()
        self.assertTrue(record.const == TheParser.ARecord.const.x)
        self.assertTrue(record.const is TheParser.ARecord.const.x)
        
    def test_inconsisent_discriminator_length(self):
        with ShouldRaise(TypeError(
            "Inconsistent discriminators: [<Discriminator 'A' (0-1)>, "
            "<Discriminator 'BB' (0-2)>]"
            )):
            class TheParser(Parser):
                class ARecord(Record):
                    prefix = Discriminator('A')
                class BRecord(Record):
                    prefix = Discriminator('BB')

    def test_inconsisent_discriminator_offset(self):
        with ShouldRaise(TypeError(
            "Inconsistent discriminators: [<Discriminator 'A' (1-2)>, "
            "<Discriminator 'B' (0-1)>]"
            )):
            class TheParser(Parser):
                class ARecord(Record):
                    data = Field(1)
                    prefix = Discriminator('A')
                class BRecord(Record):
                    prefix = Discriminator('B')
                    data = Field(2)

    def test_duplicate_record_classes(self):
        # can't tell :-(
        class TheParser(Parser):
            class ARecord(Record):
                data = Field(1)
                prefix = Discriminator('A')
            # I wish we could cause the name re-use to raise an exception
            class ARecord(Record):
                data = Field(1)
                prefix = Discriminator('B')
    
    def test_unknown_record_type_returns(self):
        # Return rather than raise exception.
        # This is optimised to be fast.
        compare(generator(
            C('fixed.UnknownRecordType',
              discriminator='C',
              line='CXX',
              args=())
            ), self.parser(['CXX']))

    def test_unknown_record_type_ignore(self):
        # Creating UnknownRecordType objects is expensive if
        # we're deliberately only creating Records for a small
        # number of rows in a file.
        compare(generator(),
                self.parser(['CXX'], parse_unknown=False))

    def test_short_lines_for_disc(self):
        compare(generator(
            C('fixed.UnknownRecordType',
              discriminator='',
              line='',
              args=())
            ), self.parser(['']))

    def test_short_line_yields(self):
        # actually, short lines just end up with blank fields
        # doing otherwise would slow things down a lot!
        compare(generator(
            self.parser.ARecord.type(prefix='A', data='')
            ), self.parser(['A']))

    def test_convertor_fail_yields(self):
        # This will be slow; avoid having it happen!
        class TheParser(Parser):
            class ARecord(Record):
                prefix = Discriminator('A')
                data = Field(1, int)
        compare(generator(
            C('fixed.ConversionError',
              args=(),
              problems=dict(data=C(
                  'fixed.Problem',
                  raw='X',
                  convert=int,
                  exception=C(
                      ValueError,
                      args=("invalid literal for int() with base 10: 'X'", ),
                      ))))
            ), TheParser(['AX']))
                
    def test_if_else_based_dispatch(self):
        expected = ['A', 'B']
        actual = []
        for record in self.parser(['AXX', 'BXX']):
            if isinstance(record, self.parser.ARecord.type):
                actual.append('A')
            elif isinstance(record, self.parser.BRecord.type):
                actual.append('B')
        compare(expected, actual)
