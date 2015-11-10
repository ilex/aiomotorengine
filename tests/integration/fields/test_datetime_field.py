#!/usr/bin/env python

from datetime import datetime

from preggy import expect
import mongoengine
from tests import async_test

import aiomotorengine
from tests.integration.base import BaseIntegrationTest


class MongoDocument(mongoengine.Document):
    meta = {'collection': 'IntegrationTestDateTimeField'}
    date = mongoengine.DateTimeField()


class MotorDocument(aiomotorengine.Document):
    __collection__ = "IntegrationTestDateTimeField"
    date = aiomotorengine.DateTimeField()


class TestDatetimeField(BaseIntegrationTest):
    @async_test
    async def test_can_integrate(self):
        mongo_document = MongoDocument(date=datetime.now()).save()

        result = await MotorDocument.objects.get(mongo_document.id)

        expect(result._id).to_equal(mongo_document.id)
        expect(result.date).to_be_like(mongo_document.date)

    @async_test
    async def test_can_integrate_backwards(self):
        motor_document = await MotorDocument.objects.create(date=datetime.now())

        result = MongoDocument.objects.get(id=motor_document._id)

        expect(result.id).to_equal(motor_document._id)
        expect(result.date).to_be_like(motor_document.date)
