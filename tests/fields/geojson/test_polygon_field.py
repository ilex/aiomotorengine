# from preggy import expect
from nose.tools import eq_, ok_
from nose.tools import assert_almost_equal as almost_eq_
from nose.tools import assert_false

from aiomotorengine import Document
from aiomotorengine import PolygonField
from tests import AsyncTestCase, async_test


class Location(Document):
    __collection__ = 'locations'
    polygon = PolygonField(required=True)
    polygon2 = PolygonField(required=False)


class TestPolygonField(AsyncTestCase):

    def setUp(self):
        super().setUp()
        self.drop_coll(Location.__collection__)

    def test_create_polygon_field(self):
        field = PolygonField(db_field="test")
        eq_(field.db_field, "test")
        eq_(field._type, 'Polygon')

    def test_create_document_with_polygon_field(self):
        loc = Location(
            polygon={
                'type': 'Polygon',
                'coordinates': [
                    [
                        [30.5233, 50.45], [30.5233, 51.45],
                        [31.5233, 51.45], [30.5233, 50.45]
                    ]
                ]
            }
        )
        ok_(loc.polygon2 is None)
        eq_(loc.polygon['type'], 'Polygon')
        eq_(len(loc.polygon['coordinates']), 1)
        almost_eq_(loc.polygon['coordinates'][0][0][0], 30.5233, places=4)
        almost_eq_(loc.polygon['coordinates'][0][2][1], 51.45, places=2)
        ok_(loc.validate())

        loc2 = Location(polygon=[
            [
                [30.5233, 50.45], [30.5233, 51.45],
                [31.5233, 51.45], [30.5233, 50.45]
            ]
        ])
        ok_(loc2.polygon2 is None)
        eq_(loc2.polygon['type'], 'Polygon')
        eq_(len(loc2.polygon['coordinates']), 1)
        almost_eq_(loc2.polygon['coordinates'][0][0][0], 30.5233, places=4)
        almost_eq_(loc2.polygon['coordinates'][0][2][1], 51.45, places=2)
        ok_(loc2.validate())

        loc3 = Location(polygon=[
            [
                [30.5233, 50.45], [30.5233, 51.45],
                [31.5233, 51.45], [30.5233, 50.45]
            ]
        ])
        ok_(loc3.validate())

    def test_polygon_field_validation(self):
        field = PolygonField(required=True)
        assert_false(field.validate('xxx'))
        assert_false(field.validate(50))
        assert_false(field.validate({}))
        assert_false(field.validate([]))
        assert_false(
            field.validate({'type': 'Wrong', 'coordinates': [50, 30]})
        )
        assert_false(
            field.validate({'type': 'Polygon', 'coordinates': {50, 30}})
        )
        assert_false(
            field.validate({'type': 'Polygon', 'coordinates': [50, 30]})
        )
        assert_false(
            field.validate({'type': 'Polygon', 'coordinates': [[[50, 30, 4]]]})
        )
        assert_false(
            field.validate({'type': 'Polygon', 'coordinates': (((50, ), ), )})
        )
        assert_false(
            field.validate({'type': 'Polygon', 'coordinates': [[['x', 30]]]})
        )
        assert_false(
            field.validate({'type': 'Polygon', 'coordinates': [[[40, 'x']]]})
        )
        assert_false(field.validate([[[40, 30]]]))
        assert_false(
            field.validate(
                {
                    'type': 'Polygon',
                    'coordinates': (([40.5, 30.3], [30.5, 30.3]), )
                }
            )
        )
        ok_(
            field.validate(
                {
                    'type': 'Polygon',
                    'coordinates': (([40.5, 30.3], [40.5, 30.3]), )
                }
            )
        )
        ok_(field.validate(None))
        ok_(field.validate({'type': 'Polygon', 'coordinates': [[[40, 30]]]}))
        ok_(field.validate({'type': 'Polygon', 'coordinates': (((40, 30), ), )}))
        ok_(
            field.validate(
                {'type': 'Polygon', 'coordinates': (([40.5, 30.3], ), )}
            )
        )

    @async_test
    async def test_polygon_field_save_and_load(self):
        loc = Location(
            polygon={
                'type': 'Polygon',
                'coordinates': [
                    [
                        [30.5233, 50.45], [30.5233, 51.45],
                        [31.5233, 51.45], [30.5233, 50.45]
                    ]
                ]
            }
        )
        await loc.save()
        ok_(loc._id is not None)

        loc2 = await Location.objects.get(id=loc._id)
        ok_(loc2.polygon2 is None)
        eq_(loc2.polygon['type'], 'Polygon')
        eq_(len(loc2.polygon['coordinates']), 1)
        almost_eq_(loc2.polygon['coordinates'][0][0][0], 30.5233, places=4)
        almost_eq_(loc2.polygon['coordinates'][0][2][1], 51.45, places=2)
        ok_(loc2.validate())

    def test_polygon_field_to_son(self):
        loc = Location(
            polygon={
                'type': 'Polygon',
                'coordinates': [
                    [
                        [30.5233, 50.45], [30.5233, 51.45],
                        [31.5233, 51.45], [30.5233, 50.45]
                    ]
                ]
            }
        )
        son = loc.to_son()
        ok_(isinstance(son, dict))
        ok_(isinstance(son['polygon'], dict))
        son = son['polygon']
        eq_(son['type'], 'Polygon')
        eq_(len(son['coordinates']), 1)
        almost_eq_(son['coordinates'][0][0][0], 30.5233, places=4)
        almost_eq_(son['coordinates'][0][2][1], 51.45, places=2)

        loc2 = Location(polygon=[
            [
                [30.5233, 50.45], [30.5233, 51.45],
                [31.5233, 51.45], [30.5233, 50.45]
            ]
        ])

        son = loc2.to_son()
        ok_(isinstance(son, dict))
        ok_(isinstance(son['polygon'], dict))
        son = son['polygon']
        eq_(son['type'], 'Polygon')
        eq_(len(son['coordinates']), 1)
        almost_eq_(son['coordinates'][0][0][0], 30.5233, places=4)
        almost_eq_(son['coordinates'][0][2][1], 51.45, places=2)
