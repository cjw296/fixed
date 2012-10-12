from unittest import TestCase

from testfixtures import Comparison as C, ShouldRaise, generator, compare

from ..import Parser, Record, Field, Discriminator, Handler, handles
import fixed

class TestHandlers(TestCase):

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

        class MyHandler(Handler):

            def __init__(self):
                self.called = []
                
            @handles(self.parser.ARecord)
            def handle_ARecord(self, source, line_no, rec):
                self.called.append(('A', source, line_no, rec))
                
            @handles(self.parser.BRecord)
            def handle_BRecord(self, source, line_no, rec):
                self.called.append(('B', source, line_no, rec))

        handler = MyHandler()
        # in reality, the following list would likely be a file
        # or a Chunker.
        source = ['AXX', 'BYY']
        handler.handle(source)
        compare(handler.called, [
            ('A', source, 1, self.parser.ARecord.type('A', 'XX')),
            ('B', source, 2, self.parser.BRecord.type('B', 'YY')),
            ])

    def test_handled_iterator(self):

        class MyHandler(Handler):

            @handles(self.parser.ARecord)
            def handle_ARecord(self, source, line_no, rec):
                return ('A', source, line_no, rec)
                
            @handles(self.parser.BRecord)
            def handle_BRecord(self, source, line_no, rec):
                return ('B', source, line_no, rec)

        handler = MyHandler()
        # in reality, the following list would likely be a file
        # or a Chunker.
        source = ['AXX', 'BYY']
        handler.handle(source)
        compare(generator(
            ('A', source, 1, self.parser.ARecord.type('A', 'XX')),
            ('B', source, 2, self.parser.BRecord.type('B', 'YY')),
            ), handler.handled(source))

    def test_missing_handler(self):
        # ignore record
        # do nothing
        class MyHandler(Handler):
            @handles(self.parser.ARecord)
            def handle_ARecord(self, source, line_no, rec):
                pass

        handler = MyHandler()
        handler.handle(['AXX', 'BYY'])
        
    def test_default_expection_handling(self):
        # raises
        class MyHandler(Handler):
            @handles(self.parser.ARecord)
            def handle_ARecord(self, source, line_no, rec):
                pass

        handler = MyHandler()

        with ShouldRaise(fixed.UnknownRecordType('C', 'YY')):
            handler.handle(['CYY'])

    def test_exception_handling_implemented(self):
        class MyHandler(Handler):
            @handles(self.parser.ARecord)
            def handle_ARecord(self, rec):
                pass
            @handles(fixed.UnknownRecordType)
            def handle_unknown(self, source, line_no, rec):
                return source, line_no, rec

        handler = MyHandler()
        source = ['CYY']
        compare(generator(
            (source, 1, C('fixed.UnknownRecordType',
                          discriminator='C',
                          line='CYY',
                          args=())),
            ), handler.handled(source))
        
    def test_ignore_unknown_rows(self):
        class MyHandler(Handler):
            # the magic line:
            parse_unknown = False
            # stuff for testing:
            @handles(self.parser.ARecord)
            def handle_ARecord(self, rec):
                pass
            @handles(fixed.UnknownRecordType)
            def handle_unknown(self, source, line_no, rec):
                return source, line_no, rec

        handler = MyHandler()
        source = ['CYY']
        compare(generator(), handler.handled(source))
        
    def test_method_handles_multiple_types(self):

        class MyHandler(Handler):

            @handles(self.parser.ARecord)
            @handles(self.parser.BRecord)
            def handle_ARecord(self, source, line_no, rec):
                return (source, line_no, rec)

        handler = MyHandler()
        source = ['AXX', 'BYY']
        handler.handle(source)
        compare(generator(
            (source, 1, self.parser.ARecord.type('A', 'XX')),
            (source, 2, self.parser.BRecord.type('B', 'YY')),
            ), handler.handled(source))
