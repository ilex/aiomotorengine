# from preggy import expect
from nose.tools import eq_, ok_
from nose.tools import assert_almost_equal as almost_eq_
from nose.tools import assert_false

from aiomotorengine import Document
from aiomotorengine import PointField
from tests import AsyncTestCase, async_test


class Location(Document):
    __collection__ = 'locations'
    point = PointField(required=True)
    point2 = PointField(required=False)


class TestPointField(AsyncTestCase):

    def setUp(self):
        super().setUp()
        self.drop_coll(Location.__collection__)

    def test_create_point_field(self):
        field = PointField(db_field="test")
        eq_(field.db_field, "test")
        eq_(field._type, 'Point')

    def test_create_document_with_point_field(self):
        loc = Location(
            point={
                'type': 'Point',
                'coordinates': [30.5233, 50.45]
            }
        )
        ok_(loc.point2 is None)
        eq_(loc.point['type'], 'Point')
        eq_(len(loc.point['coordinates']), 2)
        almost_eq_(loc.point['coordinates'][0], 30.5233, places=4)
        almost_eq_(loc.point['coordinates'][1], 50.45, places=2)
        ok_(loc.validate())

        loc2 = Location(point=[30.5233, 50.45])
        eq_(loc2.point['type'], 'Point')
        eq_(len(loc2.point['coordinates']), 2)
        almost_eq_(loc2.point['coordinates'][0], 30.5233, places=4)
        almost_eq_(loc2.point['coordinates'][1], 50.45, places=2)
        ok_(loc2.validate())

        loc3 = Location(point=[30.5233, 50.45])
        ok_(loc3.validate())

    def test_point_field_validation(self):
        field = PointField(required=True)
        assert_false(field.validate('xxx'))
        assert_false(field.validate(50))
        assert_false(field.validate({}))
        assert_false(field.validate([]))
        assert_false(
            field.validate({'type': 'Wrong', 'coordinates': [50, 30]})
        )
        assert_false(
            field.validate({'type': 'Point', 'coordinates': {50, 30}})
        )
        assert_false(
            field.validate({'type': 'Point', 'coordinates': [50, 30, 4]})
        )
        assert_false(field.validate({'type': 'Point', 'coordinates': (50, )}))
        assert_false(
            field.validate({'type': 'Point', 'coordinates': ['x', 30]})
        )
        assert_false(
            field.validate({'type': 'Point', 'coordinates': [40, 'x']})
        )
        assert_false(field.validate((40, 30)))
        ok_(field.validate(None))
        ok_(field.validate({'type': 'Point', 'coordinates': [40, 30]}))
        ok_(field.validate({'type': 'Point', 'coordinates': (40, 30)}))
        ok_(field.validate({'type': 'Point', 'coordinates': [40.5, 30.3]}))

    @async_test
    async def test_point_field_save_and_load(self):
        loc = Location(point=[30.5233, 50.45])
        await loc.save()
        ok_(loc._id is not None)

        loc2 = await Location.objects.get(id=loc._id)
        eq_(loc2.point['type'], 'Point')
        eq_(len(loc2.point['coordinates']), 2)
        almost_eq_(loc2.point['coordinates'][0], 30.5233, places=4)
        almost_eq_(loc2.point['coordinates'][1], 50.45, places=2)
        ok_(loc2.validate())

    def test_point_field_to_son(self):
        loc = Location(
            point={
                'type': 'Point',
                'coordinates': [30.5233, 50.45]
            }
        )
        son = loc.to_son()
        ok_(isinstance(son, dict))
        ok_(isinstance(son['point'], dict))
        son = son['point']
        eq_(son['type'], 'Point')
        eq_(len(son['coordinates']), 2)
        almost_eq_(son['coordinates'][0], 30.5233, places=4)
        almost_eq_(son['coordinates'][1], 50.45, places=2)

        loc2 = Location(point=[30.5233, 50.45])
        son = loc2.to_son()
        ok_(isinstance(son, dict))
        ok_(isinstance(son['point'], dict))
        son = son['point']
        eq_(son['type'], 'Point')
        eq_(len(son['coordinates']), 2)
        almost_eq_(son['coordinates'][0], 30.5233, places=4)
        almost_eq_(son['coordinates'][1], 50.45, places=2)
