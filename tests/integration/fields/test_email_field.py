#!/usr/bin/env python

from preggy import expect
import mongoengine
from tests import async_test

import aiomotorengine
from tests.integration.base import BaseIntegrationTest

COLLECTION = 'IntegrationTestEmailField'


class MongoDocument(mongoengine.Document):
    meta = {'collection': COLLECTION}
    email = mongoengine.EmailField()


class MotorDocument(aiomotorengine.Document):
    __collection__ = COLLECTION
    email = aiomotorengine.EmailField()


class TestEmailField(BaseIntegrationTest):
    @async_test
    async def test_can_integrate(self):
        mongo_document = MongoDocument(email="someone@gmail.com").save()

        result = await MotorDocument.objects.get(mongo_document.id)

        expect(result._id).to_equal(mongo_document.id)
        expect(result.email).to_equal(mongo_document.email)

    @async_test
    async def test_can_integrate_backwards(self):
        motor_document = await MotorDocument.objects.create(email="someone@gmail.com")

        result = MongoDocument.objects.get(id=motor_document._id)

        expect(result.id).to_equal(motor_document._id)
        expect(result.email).to_equal(motor_document.email)
