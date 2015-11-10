#!/usr/bin/env python

from uuid import uuid4

from preggy import expect
import mongoengine
from tests import async_test

import aiomotorengine
from tests.integration.base import BaseIntegrationTest


class MongoDocument(mongoengine.Document):
    meta = {'collection': 'IntegrationTestUUIDField'}
    uuid = mongoengine.UUIDField()


class MotorDocument(aiomotorengine.Document):
    __collection__ = "IntegrationTestUUIDField"
    uuid = aiomotorengine.UUIDField()


class TestUUIDField(BaseIntegrationTest):
    @async_test
    async def test_can_integrate(self):
        mongo_document = MongoDocument(uuid=uuid4()).save()

        result = await MotorDocument.objects.get(mongo_document.id)

        expect(result._id).to_equal(mongo_document.id)
        expect(result.uuid).to_equal(mongo_document.uuid)

    @async_test
    async def test_can_integrate_backwards(self):
        motor_document = await MotorDocument.objects.create(uuid=uuid4())

        result = MongoDocument.objects.get(id=motor_document._id)

        expect(result.id).to_equal(motor_document._id)
        expect(result.uuid).to_equal(motor_document.uuid)

    @async_test
    async def test_can_filter_properly(self):
        await MotorDocument.objects.create(uuid=uuid4())
        await MotorDocument.objects.create(uuid=uuid4())
        motor_document = await MotorDocument.objects.create(uuid=uuid4())

        results = await MotorDocument.objects.filter(uuid=motor_document.uuid).find_all()
        expect(results).to_length(1)
        expect(results[0]._id).to_equal(motor_document._id)

    @async_test
    async def test_empty_field(self):
        motor_document = await MotorDocument.objects.create()

        result = await MotorDocument.objects.get(id=motor_document._id)

        expect(result).not_to_be_null()
        expect(result.uuid).to_be_null()
