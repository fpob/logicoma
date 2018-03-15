import unittest

from logicoma import core


class TaskTestCase(unittest.TestCase):
    def test_priority_sorting(self):
        """
        Test if tasks can be sorted and are correctly sorted descending by
        their priority (highest priority first).
        """
        t1 = core.Task('1', priority=1)
        t2 = core.Task('2', priority=2)
        t3 = core.Task('3', priority=3)
        tasks_sorted = [t3, t2, t1]

        tasks_unsorted = [t1, t2, t3]
        for a, b in zip(tasks_sorted, sorted(tasks_unsorted)):
            self.assertEqual(a.url, b.url)

    def test_handler_args(self):
        """
        Test listing of function argument names.
        """
        def handler(arg1, arg2, kwarg1=None, kwarg2=None):
            pass
        t = core.Task('dummy', handler=handler)
        self.assertListEqual(t._handler_args(),
                             ['arg1', 'arg2', 'kwarg1', 'kwarg2'])


class TaskQueueTestCase(unittest.TestCase):
    def test_order(self):
        """
        Tasks with the same priority should be ordered by order of ther
        addition to the queue. For PriorityQueue which uses heap this is not
        true.
        """
        q = core.TaskQueue()
        correct_order = []
        for i in range(100):
            t = core.Task(str(i))
            q.put(t)
            correct_order.append(t)
        for a in correct_order:
            b = q.get()
            self.assertEqual(a.url, b.url)

    def test_priority(self):
        """
        Test if tasks are sorter by their priority; highest priority number is
        first in queue.
        """
        q = core.TaskQueue()
        correct_order = []
        for i in range(100):
            t = core.Task(str(i), priority=i)
            q.put(t)
            correct_order.append(t)
        for a in reversed(correct_order):
            b = q.get()
            self.assertEqual(a.url, b.url)


class HandlerTestCase(unittest.TestCase):
    def test_priority_sorting(self):
        """
        Test if handlers can be sorted and are correctly sorted descending by
        their priority (highest priority first).
        """
        dummy_func = lambda: None
        h1 = core.Handler(dummy_func, r'.*', priority=1)
        h2 = core.Handler(dummy_func, r'.*', priority=2)
        h3 = core.Handler(dummy_func, r'.*', priority=3)
        handlers_sorted = [h3, h2, h1]

        handlers_unsorted = [h1, h2, h3]
        for a, b in zip(handlers_sorted, sorted(handlers_unsorted)):
            self.assertEqual(id(a), id(b))

    def test_match(self):
        """
        Test if handlers are correctly matched to the URL.
        """
        dummy_func = lambda: None
        h = core.Handler(dummy_func, r'//google\.com/')
        self.assertTrue(h.match('//google.com/'))
        self.assertTrue(h.match('https://google.com/'))
        self.assertTrue(h.match('https://google.com/?q=query'))
        self.assertFalse(h.match('//wikipedia.org/'))

    def test_groups(self):
        """
        Test returning match groups.
        """
        dummy_func = lambda: None
        h = core.Handler(dummy_func, r'//google\.com/\?q=(?P<query>.+)')
        self.assertDictEqual(h.groups('https://google.com/?q=search'),
                             {0: '//google.com/?q=search', 1: 'search',
                              'query': 'search'})


class HandlerListTestCase(unittest.TestCase):
    def test_priority_sorting(self):
        """
        Test if handler list correctly sorting handlers by by their priority
        (highest priority first) when handlers are added via constructor.
        """
        h1 = core.Handler(lambda: None, r'.*', priority=1)
        h2 = core.Handler(lambda: None, r'.*', priority=2)
        h3 = core.Handler(lambda: None, r'.*', priority=3)
        handlers_sorted = [h3, h2, h1]

        handlers_list = core.HandlerList([h1, h2, h3])
        for a, b in zip(handlers_sorted, handlers_list):
            self.assertEqual(id(a), id(b))

    def test_priority_sorting_append(self):
        """
        Test if handler list correctly sorting handlers by by their priority
        (highest priority first) when adding with append method.
        """
        h1 = core.Handler(lambda: None, r'.*', priority=1)
        h2 = core.Handler(lambda: None, r'.*', priority=2)
        h3 = core.Handler(lambda: None, r'.*', priority=3)
        handlers_sorted = [h3, h2, h1]

        handlers_list = core.HandlerList()
        handlers_list.append(h1)
        handlers_list.append(h2)
        handlers_list.append(h3)
        for a, b in zip(handlers_sorted, handlers_list):
            self.assertEqual(id(a), id(b))

    def test_find_match(self):
        """
        Test if appropriate handler is found.
        """
        h1 = core.Handler(lambda: None, r'a')
        h2 = core.Handler(lambda: None, r'b')
        h3 = core.Handler(lambda: None, r'c')
        handler_list = core.HandlerList([h1, h2, h3])

        self.assertEqual(id(handler_list.find_match('a')), id(h1))
        self.assertIsNone(handler_list.find_match('x'))

    def test_find_match_priority(self):
        """
        Test if appropriate handler is found when multiple handlers are matched
        and should be selected handler with higher priority.
        """
        h1 = core.Handler(lambda: None, r'a', priority=1)
        h2 = core.Handler(lambda: None, r'a', priority=2)
        h3 = core.Handler(lambda: None, r'a', priority=3)
        handler_list = core.HandlerList([h1, h2, h3])

        self.assertEqual(id(handler_list.find_match('a')), id(h3))
        self.assertIsNone(handler_list.find_match('x'))
