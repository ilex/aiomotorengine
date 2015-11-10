#!/usr/bin/env python

from preggy import expect
import mongoengine
from tests import async_test

try:
    from ujson import dumps, loads
except:
    from json import dumps, loads

import aiomotorengine
from tests.integration.base import BaseIntegrationTest

COLLECTION = 'IntegrationTestJsonField'


class MongoDocument(mongoengine.Document):
    meta = {'collection': COLLECTION}
    data = mongoengine.StringField()


class MotorDocument(aiomotorengine.Document):
    __collection__ = COLLECTION
    data = aiomotorengine.JsonField()


class Other(aiomotorengine.Document):
    __collection__ = "Other_%s" % COLLECTION
    items = aiomotorengine.ListField(aiomotorengine.EmbeddedDocumentField(MotorDocument))


data = {
    "value": 10,
    "list": [1, 2, "a"],
    "dict": {
        "a": 1,
        "b": 2
    }
}


class TestStringField(BaseIntegrationTest):
    @async_test
    async def test_can_integrate(self):
        mongo_document = MongoDocument(data=dumps(data)).save()

        result = await MotorDocument.objects.get(mongo_document.id)

        expect(result._id).to_equal(mongo_document.id)
        expect(result.data).to_be_like(data)

    @async_test
    async def test_can_integrate_backwards(self):
        motor_document = await MotorDocument.objects.create(data=data)

        result = MongoDocument.objects.get(id=motor_document._id)

        expect(result.id).to_equal(motor_document._id)
        expect(loads(result.data)).to_be_like(data)

    @async_test
    async def test_gets_right_types(self):
        motor_document = await MotorDocument.objects.create(data=10)
        expect(motor_document.data).to_equal(10)

        loaded = await MotorDocument.objects.get(motor_document._id)
        expect(loaded.data).to_equal(10)

        other = await Other.objects.create()
        other.items.append(MotorDocument(data=10))
        await other.save()

        loaded = await Other.objects.get(other._id)
        expect(other.items).to_length(1)
        expect(other.items[0].data).to_equal(10)
