#!/usr/bin/env python
import unittest
import nose.tools
import asyncio
from functools import wraps

import aiomotorengine.connection
from aiomotorengine import connect


class AsyncTestCase(unittest.TestCase):
    ''' Base class for all test cases with asyncio event loop and mongodb '''
    def setUp(self, auto_connect=True):
        self.io_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        if auto_connect:
            self.db = connect(
                "test", host="localhost", port=27017, io_loop=self.io_loop
            )

    def tearDown(self):
        aiomotorengine.connection.cleanup()

    def drop_coll(self, coll):
        collection = self.db[coll]
        self.io_loop.run_until_complete(collection.drop())

    async def drop_coll_async(self, coll):
        collection = self.db[coll]
        await collection.drop()


@nose.tools.nottest
def async_test(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        async def go():
            await func(*args, **kwargs)
        self = args[0]
        self.io_loop.run_until_complete(go())
    return wrapper

#    def exec_async(self, method, *args, **kw):
#        method(callback=self.stop, *args, **kw)
#        result = self.wait()
#
#        return result['args'], result['kwargs']
