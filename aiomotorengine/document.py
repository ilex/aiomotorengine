import six

from aiomotorengine.metaclasses import DocumentMetaClass
from aiomotorengine.errors import InvalidDocumentError, LoadReferencesRequiredError


AUTHORIZED_FIELDS = ['_id', '_values']


class BaseDocument(object):
    def __init__(self, **kw):
        from aiomotorengine.fields.dynamic_field import DynamicField

        self._id = kw.pop('_id', None)
        self._values = {}

        for key, field in self._fields.items():
            if callable(field.default):
                self._values[field.db_field] = field.default()
            else:
                self._values[field.db_field] = field.default

        for key, value in kw.items():
            if key not in self._db_field_map:
                self._fields[key] = DynamicField(db_field="_%s" % key.lstrip('_'))
            self._values[key] = value

    @classmethod
    async def ensure_index(cls):
        return await cls.objects.ensure_index()

    @property
    def is_lazy(self):
        return self.__class__.__lazy__

    def is_list_field(self, field):
        from aiomotorengine.fields.list_field import ListField
        return (
            isinstance(field, ListField) or
            (isinstance(field, type) and issubclass(field, ListField))
        )

    def is_reference_field(self, field):
        from aiomotorengine.fields.reference_field import ReferenceField
        return (
            isinstance(field, ReferenceField) or
            (isinstance(field, type) and issubclass(field, ReferenceField))
        )

    def is_embedded_field(self, field):
        from aiomotorengine.fields.embedded_document_field import EmbeddedDocumentField
        return (
            isinstance(field, EmbeddedDocumentField) or (
                isinstance(field, type) and
                issubclass(field, EmbeddedDocumentField)
            )
        )

    @classmethod
    def from_son(cls, dic):
        field_values = {}
        for name, value in dic.items():
            field = cls.get_field_by_db_name(name)
            if field:
                field_values[field.name] = cls._fields[field.name].from_son(value)
            else:
                field_values[name] = value

        return cls(**field_values)

    def to_son(self):
        data = dict()

        for name, field in self._fields.items():
            value = self.get_field_value(name)
            data[field.db_field] = field.to_son(value)

        return data

    def validate(self):
        return self.validate_fields()

    def validate_fields(self):
        for name, field in self._fields.items():

            value = self.get_field_value(name)

            if field.required and field.is_empty(value):
                raise InvalidDocumentError("Field '%s' is required." % name)
            if not field.validate(value):
                raise InvalidDocumentError("Field '%s' must be valid." % name)

        return True

    async def save(self, alias=None):
        '''
        Creates or updates the current instance of this document.
        '''
        return await self.objects.save(self, alias=alias)

    async def delete(self, alias=None):
        '''
        Deletes the current instance of this Document.

        .. testsetup:: saving_delete_one

            import asyncio
            from aiomotorengine import *

            class User(Document):
                __collection__ = "UserDeletingInstance"
                name = StringField()

            io_loop = asyncio.get_event_loop()
            connect("test", host="localhost", port=27017, io_loop=io_loop)

        .. testcode:: saving_delete_one

            async def create_user():
                user = User(name="Bernardo")
                user = await user.save()
                number_of_deleted_items = await user.delete()
                assert number_of_deleted_items == 1

            io_loop.run_until_complete(create_user())
        '''
        return await self.objects.remove(instance=self, alias=alias)

    def fill_values_collection(self, collection, field_name, value):
        collection[field_name] = value

    def fill_list_values_collection(self, collection, field_name, value):
        if field_name not in collection:
            collection[field_name] = []
        collection[field_name].append(value)

    async def load_references(self, fields=None, alias=None):

        references = self.find_references(document=self, fields=fields)
        reference_count = len(references)

        if not reference_count:  # there are no references
            return {
                'loaded_reference_count': reference_count,
                'loaded_values': []
            }

        for (
            dereference_function, document_id, values_collection,
            field_name, fill_values_method
        ) in references:
            doc = await dereference_function(document_id)
            if fill_values_method is None:
                fill_values_method = self.fill_values_collection

            fill_values_method(values_collection, field_name, doc)

        return {
            'loaded_reference_count': reference_count,
            'loaded_values': values_collection
        }

    def find_references(self, document, fields=None, results=None):
        if results is None:
            results = []

        if not isinstance(document, Document):
            return results

        if fields:
            fields = [
                (field_name, document._fields[field_name])
                for field_name in fields
                if field_name in fields
            ]
        else:
            fields = [field for field in document._fields.items()]

        for field_name, field in fields:
            self.find_reference_field(document, results, field_name, field)
            self.find_list_field(document, results, field_name, field)
            self.find_embed_field(document, results, field_name, field)

        return results

    def find_reference_field(self, document, results, field_name, field):
        if self.is_reference_field(field):
            value = document._values.get(field_name, None)

            if value is not None:
                results.append([
                    field.reference_type.objects.get,
                    value,
                    document._values,
                    field_name,
                    None
                ])

    def find_list_field(self, document, results, field_name, field):
        from aiomotorengine.fields.reference_field import ReferenceField
        if self.is_list_field(field):
            values = document._values.get(field_name)
            if values:
                document_type = values[0].__class__
                if isinstance(field._base_field, ReferenceField):
                    document_type = field._base_field.reference_type
                    for value in values:
                        results.append([
                            document_type.objects.get,
                            value,
                            document._values,
                            field_name,
                            self.fill_list_values_collection
                        ])
                    document._values[field_name] = []
                else:
                    self.find_references(document=document_type, results=results)

    def find_embed_field(self, document, results, field_name, field):
        if self.is_embedded_field(field):
            value = document._values.get(field_name, None)
            if value:
                self.find_references(document=value, results=results)

    def get_field_value(self, name):
        if name not in self._fields:
            raise ValueError("Field %s not found in instance of %s." % (
                name,
                self.__class__.__name__
            ))

        field = self._fields[name]
        value = field.get_value(self._values.get(name, None))

        return value

    def __getattribute__(self, name):
        # required for the next test
        if name in ['_fields']:
            return object.__getattribute__(self, name)

        if name in self._fields:
            field = self._fields[name]
            is_reference_field = self.is_reference_field(field)
            value = field.get_value(self._values.get(name, None))

            if is_reference_field and value is not None and not isinstance(value, field.reference_type):
                message = "The property '%s' can't be accessed before calling 'load_references'" + \
                    " on its instance first (%s) or setting __lazy__ to False in the %s class."

                raise LoadReferencesRequiredError(
                    message % (name, self.__class__.__name__, self.__class__.__name__)
                )

            return value

        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        from aiomotorengine.fields.dynamic_field import DynamicField

        if name not in AUTHORIZED_FIELDS and name not in self._fields:
            self._fields[name] = DynamicField(db_field="_%s" % name)

        if name in self._fields:
            self._values[name] = value
            return

        object.__setattr__(self, name, value)

    @classmethod
    def get_field_by_db_name(cls, name):
        for field_name, field in cls._fields.items():
            if name == field.db_field or name.lstrip("_") == field.db_field:
                return field
        return None

    @classmethod
    def get_fields(cls, name, fields=None):
        from aiomotorengine import EmbeddedDocumentField, ListField
        from aiomotorengine.fields.dynamic_field import DynamicField

        if fields is None:
            fields = []

        if '.' not in name:
            dyn_field = DynamicField(db_field="_%s" % name)
            fields.append(cls._fields.get(name, dyn_field))
            return fields

        field_values = name.split('.')
        dyn_field = DynamicField(db_field="_%s" % field_values[0])
        obj = cls._fields.get(field_values[0], dyn_field)
        fields.append(obj)

        if isinstance(obj, (EmbeddedDocumentField, )):
            obj.embedded_type.get_fields(".".join(field_values[1:]), fields=fields)

        if isinstance(obj, (ListField, )):
            obj.item_type.get_fields(".".join(field_values[1:]), fields=fields)

        return fields


class Document(six.with_metaclass(DocumentMetaClass, BaseDocument)):
    '''
    Base class for all documents specified in MotorEngine.
    '''
    pass
