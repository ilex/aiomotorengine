#!/usr/bin/env python

import aiomotorengine
import mongoengine

from tests import AsyncTestCase


class BaseIntegrationTest(AsyncTestCase):
    def setUp(self, auto_connect=True):
        # super(AsyncTestCase, self).setUp(auto_connect=auto_connect)
        super().setUp(auto_connect=False)
        if auto_connect:
            self.db = aiomotorengine.connect(
                "test", host="localhost", port=27017, io_loop=self.io_loop
            )
            mongoengine.connect("test", host="localhost", port=27017)

    def tearDown(self):
        aiomotorengine.connection.cleanup()
        super().tearDown()
