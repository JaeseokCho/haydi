
from domain import Domain, DomainIterator
from random import randint

from factory import IteratorFactory

from copy import copy


class Range(Domain):

    exact_size = True

    def __init__(self, start, end=None, step=None, name=None):
        if end is None:
            end = start
            start = 0
        end = max(start, end)
        if step is None:
            step = 1
        else:
            step = step
            assert step >= 0

        if step == 1 and end == 1:
            size = end
        else:
            size = (end - start) / step

        super(Range, self).__init__(size, True, name)

        self.start = start
        self.end = end
        self.step = step

    def iterate(self):
        return IteratorFactory(RangeIterator, self)

    def generate_one(self):
        if self.step == 1:
            return randint(self.start, self.end - 1)
        else:
            return randint(0, self.size - 1) * self.step

    def __repr__(self):
        return "Range({},{},{})".format(self.start, self.end, self.step)


class RangeIterator(DomainIterator):

    def __init__(self, domain):
        super(RangeIterator, self).__init__(domain)
        self.value = domain.start

    def skip(self, start_index, count):
        start = self.domain.start + start_index
        end = start + count

        return RangeIterator(Range(start, end))

    def copy(self):
        return copy(self)

    def reset(self):
        self.value = self.domain.start

    def next(self):
        v = self.value
        if v < self.domain.end:
            self.value += self.domain.step
            return v
        raise StopIteration()

    def __repr__(self):
        return "{} iterator".format(str(self.domain))

    def set(self, index):
        self.value = self.domain.start + self.domain.step * index
