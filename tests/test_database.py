#!/usr/bin/env python

from preggy import expect
import motor.motor_asyncio

from aiomotorengine import connect, disconnect
from tests import AsyncTestCase, async_test


class TestDatabase(AsyncTestCase):

    @async_test
    async def test_database_ping(self):
        db = connect("test", host="localhost", port=27017,
                     io_loop=self.io_loop)

        res = await db.ping()
        ping_result = res['ok']
        expect(ping_result).to_equal(1.0)

        disconnect()

    def test_database_returns_collection_when_asked_for_a_name(self):
        db = connect("test", host="localhost", port=27017, io_loop=self.io_loop)

        expect(db.something).to_be_instance_of(
            motor.motor_asyncio.AsyncIOMotorCollection
        )
