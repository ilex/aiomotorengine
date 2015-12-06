from aiomotorengine.fields.geojson.geo_json_base_field import GeoJsonBaseField


class LineStringField(GeoJsonBaseField):
    '''
    A GeoJSON field storing a line of longitude and latitude coordinates.

    The data is represented as:

    .. code-block:: js

        {
            "type" : "LineString",
            "coordinates" : [[x1, y1], [x1, y1] ... [xn, yn]]
        }

    You can either pass a dict with the full information or a list of points.

    .. note::

        Always list coordinates in **longitude**, **latitude** order.

    Usage:

    .. testcode:: modeling_fields

        class Location(Document):
            line = LineStringField(required=True)

        async def go():
            loc = Location(line={
                'type': 'LineString',
                'coordinates': [
                    [50.45, 30.5233],
                    [20.45, 30.5233],
                    [10.45, 50.5233]
                ]
            })
            await loc.save()

            loc2 = Location(polygon=[
                [50.45, 30.5233],
                [20.45, 30.5233],
                [10.45, 50.5233],
            ])
            await loc2.save()

    Available arguments (apart from those in `BaseField`):

    * `auto_index` - for now it has no effect and you should create index manually

    Requires mongodb >= 2.4

    .. versionadded:: 0.8
    '''
    _type = "LineString"

    def validate(self, value):
        if value is None:
            return True

        if (
            super().validate(value) and
            self._validate_linestring(value['coordinates'])
        ):
            return True

        return False
