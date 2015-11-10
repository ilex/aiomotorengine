import sys

from pymongo.errors import DuplicateKeyError
from easydict import EasyDict as edict
from bson.objectid import ObjectId

from aiomotorengine import ASCENDING
from aiomotorengine.aggregation.base import Aggregation
from aiomotorengine.connection import get_connection
from aiomotorengine.errors import UniqueKeyViolationError

DEFAULT_LIMIT = 1000


class QuerySet(object):
    def __init__(self, klass):
        self.__klass__ = klass
        self._filters = {}
        self._limit = None
        self._skip = None
        self._order_fields = []

    @property
    def is_lazy(self):
        return self.__klass__.__lazy__

    def coll(self, alias=None):
        if alias is not None:
            conn = get_connection(alias=alias)
        elif self.__klass__.__alias__ is not None:
            conn = get_connection(alias=self.__klass__.__alias__)
        else:
            conn = get_connection()

        return conn[self.__klass__.__collection__]

    async def create(self, alias=None, **kwargs):
        '''
        Creates and saved a new instance of the document.

        .. testsetup:: saving_create

            import asyncio
            from aiomotorengine import *

            class User(Document):
                __collection__ = "UserCreatingInstances"
                name = StringField()

            io_loop = asyncio.get_event_loop()
            connect("test", host="localhost", port=27017, io_loop=io_loop)

        .. testcode:: saving_create

            async def create_user():
                user = await User.objects.create(name="Bernardo")
                assert user.name == "Bernardo"

            io_loop.run_until_complete(create_user())
        '''
        document = self.__klass__(**kwargs)
        return await self.save(document=document, alias=alias)

    def update_field_on_save_values(self, document, creating):
        for field_name, field in self.__klass__._fields.items():
            if field.on_save is not None:
                setattr(document, field_name, field.on_save(document, creating))

    async def save(self, document, alias=None):
        if self.validate_document(document):
            await self.ensure_index(alias=alias)
            return await self.save_document(document, alias=alias)

    async def save_document(self, document, alias=None):
        ''' Insert or update document '''
        self.update_field_on_save_values(document, document._id is not None)
        doc = document.to_son()

        if document._id is not None:
            await self.coll(alias).update({'_id': document._id}, doc)
        else:
            try:
                doc_id = await self.coll(alias).insert(doc)
            except DuplicateKeyError as e:
                raise UniqueKeyViolationError.from_pymongo(
                    str(e), self.__klass__
                )
            document._id = doc_id
        return document

    def validate_document(self, document):
        if not isinstance(document, self.__klass__):
            raise ValueError("This queryset for class '%s' can't save an instance of type '%s'." % (
                self.__klass__.__name__,
                document.__class__.__name__,
            ))

        return document.validate()

    async def bulk_insert(self, documents, callback=None, alias=None):
        '''
        Inserts all documents passed to this method in one go.
        '''

        is_valid = True
        docs_to_insert = []

        for document_index, document in enumerate(documents):
            try:
                is_valid = is_valid and self.validate_document(document)
            except Exception:
                err = sys.exc_info()[1]
                raise ValueError("Validation for document %d in the documents you are saving failed with: %s" % (
                    document_index,
                    str(err)
                ))

            if not is_valid:
                return

            docs_to_insert.append(document.to_son())

        if not is_valid:
            return

        doc_ids = await self.coll(alias).insert(docs_to_insert)

        for object_index, object_id in enumerate(doc_ids):
            documents[object_index]._id = object_id
        return documents

    def transform_definition(self, definition):
        from aiomotorengine.fields.base_field import BaseField

        result = {}

        for key, value in definition.items():
            if isinstance(key, (BaseField, )):
                result[key.db_field] = value
            else:
                result[key] = value

        return result

    async def update(self, definition, alias=None):

        definition = self.transform_definition(definition)

        update_filters = {}
        if self._filters:
            update_filters = self.get_query_from_filters(self._filters)

        update_arguments = dict(
            spec=update_filters,
            document={'$set': definition},
            multi=True,
        )
        res = await self.coll(alias).update(**update_arguments)
        return edict({
            "count": int(res['n']),
            "updated_existing": res['updatedExisting']
        })

    # TODO rewrite docstring
    async def delete(self, alias=None):
        '''
        Removes all instances of this document that match the specified filters (if any).

        .. testsetup:: saving_delete

            import asyncio
            from aiomotorengine import *

            class User(Document):
                __collection__ = "UserDeletingInstances"
                name = StringField()

            io_loop = asyncio.get_event_loop()
            connect("test", host="localhost", port=27017, io_loop=io_loop)

        .. testcode:: saving_delete

            async def saving_delete():
                user = User(name="Bernardo")
                await user.save()

                number_of_deleted_items = await User.objects.filter(name="Bernardo").delete()
                assert number_of_deleted_items == 1

            io_loop.run_until_complete(saving_delete())
        '''

        return await self.remove(alias=alias)

    async def remove(self, instance=None, alias=None):

        if instance is not None:
            if hasattr(instance, '_id') and instance._id:
                res = await self.coll(alias).remove(instance._id)
        else:
            if self._filters:
                remove_filters = self.get_query_from_filters(self._filters)
                res = await self.coll(alias).remove(remove_filters)
            else:
                res = await self.coll(alias).remove()
        return res['n']

    async def get(self, id=None, alias=None, **kwargs):
        '''
        Gets a single item of the current queryset collection using it's id.

        In order to query a different database, please specify the `alias` of the database to query.
        '''

        from aiomotorengine import Q

        if id is None and not kwargs:
            raise RuntimeError("Either an id or a filter must be provided to get")

        if id is not None:
            if not isinstance(id, ObjectId):
                id = ObjectId(id)

            filters = {
                "_id": id
            }
        else:
            filters = Q(**kwargs)
            filters = self.get_query_from_filters(filters)

        instance = await self.coll(alias).find_one(filters)
        if instance is None:
            return None
        else:
            doc = self.__klass__.from_son(instance)
            if self.is_lazy:
                return doc
            else:
                await doc.load_references()
                return doc

    def get_query_from_filters(self, filters):
        if not filters:
            return {}

        query = filters.to_query(self.__klass__)
        return query

    def _get_find_cursor(self, alias):
        find_arguments = {}

        if self._order_fields:
            find_arguments['sort'] = self._order_fields

        if self._limit:
            find_arguments['limit'] = self._limit

        if self._skip:
            find_arguments['skip'] = self._skip

        query_filters = self.get_query_from_filters(self._filters)

        return self.coll(alias).find(query_filters, **find_arguments)

    def filter(self, *arguments, **kwargs):
        '''
        Filters a queryset in order to produce a different set of document from subsequent queries.

        Usage::

            users = await User.objects.filter(first_name="Bernardo").filter(last_name="Bernardo").find_all()
            # or
            users = await User.objects.filter(first_name="Bernardo", starting_year__gt=2010).find_all()

        The available filter options are the same as used in MongoEngine.
        '''
        from aiomotorengine.query_builder.node import Q, QCombination, QNot
        from aiomotorengine.query_builder.transform import validate_fields

        if (
            arguments and len(arguments) == 1 and
            isinstance(arguments[0], (Q, QNot, QCombination))
        ):
            if self._filters:
                self._filters = self._filters & arguments[0]
            else:
                self._filters = arguments[0]
        else:
            validate_fields(self.__klass__, kwargs)
            if self._filters:
                self._filters = self._filters & Q(**kwargs)
            else:
                if (
                    arguments and len(arguments) == 1
                    and isinstance(arguments[0], dict)
                ):
                    self._filters = Q(arguments[0])
                else:
                    self._filters = Q(**kwargs)

        return self

    def filter_not(self, *arguments, **kwargs):
        '''
        Filters a queryset to negate all the filters passed in subsequent queries.

        Usage::

            objects = User.objects.filter_not(first_name="Bernardo")
            objects = objects.filter_not(last_name="Bernardo")
            users = await objects.find_all()
            # or
            objects = User.objects.filter_not(
            first_name="Bernardo", starting_year__gt=2010
            )
            users = await objects.find_all()

        The available filter options are the same as used in MongoEngine.
        '''
        from aiomotorengine.query_builder.node import Q, QCombination, QNot

        if arguments and len(arguments) == 1 and isinstance(arguments[0], (Q, QCombination)):
            self._filters = QNot(arguments[0])
        else:
            self._filters = QNot(Q(**kwargs))

        return self

    def skip(self, skip):
        '''
        Skips N documents before returning in subsequent queries.

        Usage::

            users = await User.objects.skip(20).limit(10).find_all()
            # even if there are 100s of users,
            # only users 20-30 will be returned
        '''

        self._skip = skip
        return self

    def limit(self, limit):
        '''
        Limits the number of documents to return in subsequent queries.

        Usage::

            users = await User.objects.limit(10).find_all()
            # even if there are 100s of users,
            # only first 10 will be returned
        '''

        self._limit = limit
        return self

    def order_by(self, field_name, direction=ASCENDING):
        '''
        Specified the order to be used when returning documents in subsequent queries.

        Usage::

            from aiomotorengine import DESCENDING  # or ASCENDING

            users = await User.objects.order_by(
                'first_name', direction=DESCENDING
            ).find_all()
        '''

        from aiomotorengine.fields.base_field import BaseField
        from aiomotorengine.fields.list_field import ListField

        if isinstance(field_name, (ListField, )):
            raise ValueError("Can't order by a list field. If you meant to order by the size of the list, please use either an Aggregation Pipeline query (look for Document.objects.aggregate) or create an IntField with the size of the list field in your Document.")

        if isinstance(field_name, (BaseField, )):
            field_name = field_name.name

        if field_name not in self.__klass__._fields:
            raise ValueError("Invalid order by field '%s': Field not found in '%s'." % (field_name, self.__klass__.__name__))

        field = self.__klass__._fields[field_name]
        self._order_fields.append((field.db_field, direction))
        return self

    async def find_all(self, lazy=None, alias=None):
        '''
        Returns a list of items in the current queryset collection that match specified filters (if any).

        In order to query a different database, please specify the `alias` of the database to query.

        Usage::

            result = await User.objects.find_all()
            # do something with result
            # users is None if no users found
        '''
        to_list_arguments = {}
        if self._limit is not None:
            to_list_arguments['length'] = self._limit
        else:
            to_list_arguments['length'] = DEFAULT_LIMIT

        cursor = self._get_find_cursor(alias=alias)

        self._filters = {}

        docs = await cursor.to_list(**to_list_arguments)

        result = []
        for doc in docs:
            obj = self.__klass__.from_son(doc)

            if (lazy is not None and not lazy) or not obj.is_lazy:
                await obj.load_references(obj._fields)

            result.append(obj)

        return result

    async def count(self, alias=None):
        '''
        Returns the number of documents in the collection that match the specified filters, if any.
        '''
        cursor = self._get_find_cursor(alias=alias)
        self._filters = {}
        return await cursor.count()

    @property
    def aggregate(self):
        return Aggregation(self)

    async def ensure_index(self, alias=None):
        indexes = []
        for field_name, field in list(self.__klass__._fields.items()):
            if field.unique:
                indexes.append(field.db_field)

        for index in indexes:
            await self.coll(alias).ensure_index(
                index, unique=True, alias=alias)
        return len(indexes)
