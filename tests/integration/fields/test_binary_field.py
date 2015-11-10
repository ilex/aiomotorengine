#!/usr/bin/env python

# -*- coding: utf-8 -*-

import six
from preggy import expect
import mongoengine
from tests import async_test

import aiomotorengine
from tests.integration.base import BaseIntegrationTest

COLLECTION = "IntegrationTestBinaryField"


class MongoDocument(mongoengine.Document):
    meta = {'collection': COLLECTION}
    byte = mongoengine.BinaryField()


class MotorDocument(aiomotorengine.Document):
    __collection__ = COLLECTION
    byte = aiomotorengine.BinaryField()


class TestBinaryField(BaseIntegrationTest):
    @async_test
    async def test_can_integrate(self):
        mongo_document = MongoDocument(byte=six.b("some_string")).save()

        result = await MotorDocument.objects.get(mongo_document.id)

        expect(result._id).to_equal(mongo_document.id)
        expect(result.byte).to_equal(mongo_document.byte)

    @async_test
    async def test_can_integrate_backwards(self):
        motor_document = await MotorDocument.objects.create(byte=six.b("other_string"))

        result = MongoDocument.objects.get(id=motor_document._id)

        expect(result.id).to_equal(motor_document._id)
        expect(result.byte).to_equal(motor_document.byte)
