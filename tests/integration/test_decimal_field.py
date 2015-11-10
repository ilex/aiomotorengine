#!/usr/bin/env python

from decimal import Decimal

from preggy import expect
import mongoengine

import aiomotorengine
from tests.integration.base import BaseIntegrationTest
from tests import async_test

COLLECTION = 'IntegrationTestDecimalField'


class MongoDocument(mongoengine.Document):
    meta = {'collection': COLLECTION}
    number = mongoengine.DecimalField()


class MotorDocument(aiomotorengine.Document):
    __collection__ = COLLECTION
    number = aiomotorengine.DecimalField()


class TestIntField(BaseIntegrationTest):
    @async_test
    async def test_can_integrate(self):
        mongo_document = MongoDocument(number=Decimal("10.53")).save()

        result = await MotorDocument.objects.get(mongo_document.id)

        expect(result._id).to_equal(mongo_document.id)
        expect(result.number).to_equal(mongo_document.number)

    @async_test
    async def test_can_integrate_backwards(self):
        motor_document = await MotorDocument.objects.create(number=Decimal("10.53"))

        result = MongoDocument.objects.get(id=motor_document._id)

        expect(result.id).to_equal(motor_document._id)
        expect(result.number).to_equal(motor_document.number)
