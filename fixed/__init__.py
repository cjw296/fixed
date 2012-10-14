# Copyright (c) 2012 Simplistix Ltd
# See license.txt for license details.

from collections import namedtuple
from operator import attrgetter

from fields import Field, Discriminator, Skip
from constants import Constant, one_of, all
from exceptions import Problem, FixedException, UnknownRecordType, ConversionError
from records import Record
from parser import Parser
from handler import Handler, handles

# helpers

class Chunker(object):

    def __init__(self, stream, width):
        self.stream = stream
        self.width = width

    def __iter__(self):
        while True:
            data = self.stream.read(self.width)
            if len(data) < self.width:
                break
            yield data
