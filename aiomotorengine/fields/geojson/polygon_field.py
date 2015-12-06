from aiomotorengine.fields.geojson.geo_json_base_field import (
    GeoJsonBaseField
)


class PolygonField(GeoJsonBaseField):
    '''
    A GeoJSON field storing a polygon of longitude and latitude coordinates.

    The data is represented as:

    .. code-block:: js

        {
            'type' : 'Polygon',
            'coordinates' : [
                [[x1, y1], [x1, y1], ... [xn, yn]],
                [[x1, y1], [x1, y1], ... [xn, yn]]
            ]
        }

    You can either pass a dict with the full information or a list
    of LineStrings. The first LineString being the outside and the rest being
    holes.

    .. note::

        Always list coordinates in **longitude**, **latitude** order.

    The first and last coordinates must match in order to close the polygon.

    For Polygons with multiple rings:

        * The first described ring must be the exterior ring.
        * The exterior ring cannot self-intersect.
        * Any interior ring must be entirely contained by the outer ring.
        * Interior rings cannot intersect or overlap each other. Interior rings
          cannot share an edge.

    Usage:

    .. testcode:: modeling_fields

        class Location(Document):
            polygon = PolygonField(required=True)

        async def go():
            # create polygon without holes (only one exterior ring)
            loc = Location(polygon={
                'type': 'Polygon',
                'coordinates': [
                    [
                        [50.45, 30.5233],
                        [20.45, 30.5233],
                        [10.45, 50.5233],
                        [50.45, 30.5233]
                    ]
                ]
            })
            await loc.save()

            loc2 = Location(polygon=[
                [
                    [50.45, 30.5233],
                    [20.45, 30.5233],
                    [10.45, 50.5233],
                    [50.45, 30.5233]
                ]
            ])
            await loc2.save()

    Available arguments (apart from those in `BaseField`):

    * `auto_index` - for now it has no effect and you should create
      index manually

    Requires mongodb >= 2.4

    .. versionadded:: 0.8
    '''
    _type = 'Polygon'

    def validate(self, value):
        if value is None:
            return True

        if (
            super().validate(value) and
            self._validate_polygon(value['coordinates'])
        ):
            return True

        return False
