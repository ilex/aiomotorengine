from aiomotorengine.fields.geojson.geo_json_base_field import (
    GeoJsonBaseField
)


class PointField(GeoJsonBaseField):
    '''
    A GeoJSON field storing a longitude and latitude coordinate.

    The data is represented as:

    .. code-block:: js

        {
            'type' : 'Point',
            'coordinates' : [x, y]
        }

    You can either pass a dict with the full information or a list
    to set the value.

    .. note::

        Always list coordinates in **longitude**, **latitude** order.

    Usage:

    .. testcode:: modeling_fields

        class Location(Document):
            point = PointField(required=True)

        async def go():
            loc = Location(point={
                'type': 'Point',
                'coordinates': [50.45, 30.5233]
            })
            await loc.save()

            loc2 = Location(point=[50.45, 30.5233])
            await loc2.save()

    Available arguments (apart from those in `BaseField`):

    * `auto_index` - for now it has no effect and you should create index manually

    Requires mongodb >= 2.4

    .. versionadded:: 0.8
    '''
    _type = 'Point'
    # _geo_index = pymongo.GEOSPHERE

    def validate(self, value):
        if value is None:
            return True

        if (
            super().validate(value) and
            self._validate_point(value['coordinates'])
        ):
            return True

        return False
