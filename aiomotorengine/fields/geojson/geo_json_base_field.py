from aiomotorengine.fields.base_field import BaseField


class GeoJsonBaseField(BaseField):
    '''
    A geo json field storing a geojson style object.

    .. versionadded:: 0.8
    '''
    _type = "GeoBase"

    def __init__(self, auto_index=True, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_value(self, value):
        if value is None:
            return value

        if isinstance(value, (list, tuple)):
            return {
                'type': self._type,
                'coordinates': value
            }

        return value

    def _validate_point(self, value):
        ''' Inspect value = [x,y] '''

        if not isinstance(value, (list, tuple)):
            return False
        elif not len(value) == 2:
            return False
        elif (not isinstance(value[0], (float, int)) or
              not isinstance(value[1], (float, int))):
            return False

        return True

    def _validate_linestring(self, value):
        ''' Validates a LineString '''

        if not isinstance(value, (list, tuple)):
            return False

        # Quick and dirty validator
        try:
            value[0][0]
        except:
            return False

        for val in value:
            if not self._validate_point(val):
                return False

        return True

    def _validate_polygon(self, value):
        ''' Validate a Polygon '''
        if not isinstance(value, (list, tuple)):
            return False

        # Quick and dirty validator
        try:
            value[0][0][0]
        except:
            return False

        for val in value:
            if not self._validate_linestring(val):
                return False
            if val[0] != val[-1]:
                # 'LineStrings must start and end at the same point'
                return False

        return True

    def validate(self, value):
        '''
        Base implementation of validation

        Check `type` field and presence of `coordinates` field

        .. note:: Subclasses should implement validation of `coordinates` field
        '''
        # if value is None:
        #    return True

        if isinstance(value, dict):
            if (
                'type' in value and value['type'] == self._type and
                'coordinates' in value
            ):
                return True
            else:
                return False

        return False
