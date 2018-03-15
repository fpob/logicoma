import unittest

from logicoma import utils


class FilterChainTestCase:
    def test_empty(self):
        fc = FilterChain()
        self.assertTrue(fc(None))

    def test_filter(self):
        fc = FilterChain()
        fc.append(lambda i: i > 1)
        fc.append(lambda i: i % 2 == 0)
        self.assertFalse(fc(0))
        self.assertFalse(fc(1))
        self.assertTrue(fc(2))
        self.assertTrue(fc(4))
