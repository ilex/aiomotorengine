#!/usr/bin/env python

from preggy import expect
import mongoengine
from tests import async_test

import aiomotorengine
from tests.integration.base import BaseIntegrationTest

COLLECTION = 'IntegrationTestIntField'


class MongoDocument(mongoengine.Document):
    meta = {'collection': COLLECTION}
    number = mongoengine.IntField()


class MotorDocument(aiomotorengine.Document):
    __collection__ = COLLECTION
    number = aiomotorengine.IntField()


class TestIntField(BaseIntegrationTest):
    @async_test
    async def test_can_integrate(self):
        mongo_document = MongoDocument(number=10).save()

        result = await MotorDocument.objects.get(mongo_document.id)

        expect(result._id).to_equal(mongo_document.id)
        expect(result.number).to_equal(mongo_document.number)

    @async_test
    async def test_can_integrate_backwards(self):
        motor_document = await MotorDocument.objects.create(number=10)

        result = MongoDocument.objects.get(id=motor_document._id)

        expect(result.id).to_equal(motor_document._id)
        expect(result.number).to_equal(motor_document.number)

    @async_test
    async def test_empty_field(self):
        motor_document = await MotorDocument.objects.create()

        result = await MotorDocument.objects.get(id=motor_document._id)

        expect(result).not_to_be_null()
        expect(result.number).to_be_null()
