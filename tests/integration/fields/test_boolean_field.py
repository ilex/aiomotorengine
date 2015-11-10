#!/usr/bin/env python

from preggy import expect
import mongoengine
from tests import async_test

import aiomotorengine
from tests.integration.base import BaseIntegrationTest


class MongoDocument(mongoengine.Document):
    meta = {'collection': 'IntegrationTestBooleanField'}
    is_active = mongoengine.BooleanField()


class MotorDocument(aiomotorengine.Document):
    __collection__ = "IntegrationTestBooleanField"
    is_active = aiomotorengine.BooleanField()


class TestBooleanField(BaseIntegrationTest):
    @async_test
    async def test_can_integrate(self):
        mongo_document = MongoDocument(is_active=True).save()

        result = await MotorDocument.objects.get(mongo_document.id)

        expect(result._id).to_equal(mongo_document.id)
        expect(result.is_active).to_be_true()

    @async_test
    async def test_can_integrate_backwards(self):
        motor_document = await MotorDocument.objects.create(is_active=True)

        result = MongoDocument.objects.get(id=motor_document._id)

        expect(result.id).to_equal(motor_document._id)
        expect(result.is_active).to_be_true()
