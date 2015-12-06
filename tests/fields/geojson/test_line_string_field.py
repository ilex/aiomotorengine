# from preggy import expect
from nose.tools import eq_, ok_
from nose.tools import assert_almost_equal as almost_eq_
from nose.tools import assert_false

from aiomotorengine import Document
from aiomotorengine import LineStringField
from tests import AsyncTestCase, async_test


class Location(Document):
    __collection__ = 'locations'
    line = LineStringField(required=True)
    line2 = LineStringField(required=False)


class TestLineStringField(AsyncTestCase):

    def setUp(self):
        super().setUp()
        self.drop_coll(Location.__collection__)

    def test_create_point_field(self):
        field = LineStringField(db_field="test")
        eq_(field.db_field, "test")
        eq_(field._type, 'LineString')

    def test_create_document_with_line_string_field(self):
        loc = Location(
            line={
                'type': 'LineString',
                'coordinates': [
                    (30.5233, 50.45),
                    [31.5233, 51.45],
                    [32.5233, 51.45]
                ]
            }
        )
        ok_(loc.line2 is None)
        eq_(loc.line['type'], 'LineString')
        eq_(len(loc.line['coordinates']), 3)
        almost_eq_(loc.line['coordinates'][0][1], 50.45, places=2)
        almost_eq_(loc.line['coordinates'][1][0], 31.5233, places=4)
        ok_(loc.validate())

        loc2 = Location(
            line=[
                (30.5233, 50.45),
                [31.5233, 51.45],
                [32.5233, 51.45]
            ]
        )
        ok_(loc2.line2 is None)
        eq_(loc2.line['type'], 'LineString')
        eq_(len(loc2.line['coordinates']), 3)
        almost_eq_(loc2.line['coordinates'][0][1], 50.45, places=2)
        almost_eq_(loc2.line['coordinates'][1][0], 31.5233, places=4)
        ok_(loc2.validate())

        loc3 = Location(
            line=[
                (30.5233, 50.45),
                [31.5233, 51.45],
                [32.5233, 51.45]
            ]
        )
        ok_(loc3.validate())

    def test_line_string_field_validation(self):
        field = LineStringField(required=True)
        assert_false(field.validate('xxx'))
        assert_false(field.validate(50))
        assert_false(field.validate({}))
        assert_false(field.validate([]))
        assert_false(
            field.validate(
                {'type': 'Wrong', 'coordinates': [[50, 30], [51, 31]]}
            )
        )
        assert_false(
            field.validate({'type': 'LineString', 'coordinates': {50, 30}})
        )
        assert_false(
            field.validate(
                {'type': 'LineString', 'coordinates': [[50, 30, 4], ]}
            )
        )
        assert_false(
            field.validate(
                {'type': 'LineString', 'coordinates': []}
            )
        )
        assert_false(
            field.validate({'type': 'LineString', 'coordinates': [(50, )]})
        )
        assert_false(
            field.validate({'type': 'LineString', 'coordinates': [['x', 30]]})
        )
        assert_false(
            field.validate({'type': 'LineString', 'coordinates': [[40, 'x']]})
        )
        assert_false(field.validate([(40, 30), [41, 34]]))
        ok_(field.validate(None))
        ok_(field.validate({'type': 'LineString', 'coordinates': [[40, 30]]}))
        ok_(field.validate(
            {'type': 'LineString', 'coordinates': ((40, 30), (25, 14))}
        ))
        ok_(field.validate(
            {'type': 'LineString', 'coordinates': [[40.5, 30.3], [40, 12]]}
        ))

    @async_test
    async def test_line_string_field_save_and_load(self):
        loc = Location(
            line=[
                (30.5233, 50.45),
                [31.5233, 51.45],
                [32.5233, 51.45]
            ]
        )
        await loc.save()
        ok_(loc._id is not None)

        loc2 = await Location.objects.get(id=loc._id)
        ok_(loc2.line2 is None)
        eq_(loc2.line['type'], 'LineString')
        eq_(len(loc2.line['coordinates']), 3)
        almost_eq_(loc2.line['coordinates'][0][1], 50.45, places=2)
        almost_eq_(loc2.line['coordinates'][1][0], 31.5233, places=4)
        ok_(loc2.validate())

    def test_line_string_field_to_son(self):
        loc = Location(
            line={
                'type': 'LineString',
                'coordinates': [
                    (30.5233, 50.45),
                    [31.5233, 51.45],
                    [32.5233, 51.45]
                ]
            }
        )
        son = loc.to_son()
        ok_(isinstance(son, dict))
        ok_(isinstance(son['line'], dict))
        son = son['line']
        eq_(son['type'], 'LineString')
        eq_(len(son['coordinates']), 3)
        almost_eq_(son['coordinates'][0][1], 50.45, places=2)
        almost_eq_(son['coordinates'][1][0], 31.5233, places=4)

        loc2 = Location(
            line=[
                (30.5233, 50.45),
                [31.5233, 51.45],
                [32.5233, 51.45]
            ]
        )

        son = loc2.to_son()
        ok_(isinstance(son, dict))
        ok_(isinstance(son['line'], dict))
        son = son['line']
        eq_(son['type'], 'LineString')
        eq_(len(son['coordinates']), 3)
        almost_eq_(son['coordinates'][0][1], 50.45, places=2)
        almost_eq_(son['coordinates'][1][0], 31.5233, places=4)
