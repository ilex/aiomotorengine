Modeling
========

.. py:module:: aiomotorengine.document
.. py:module:: aiomotorengine.fields.base_field
.. py:module:: aiomotorengine.fields.string_field
.. py:module:: aiomotorengine.fields.datetime_field
.. py:module:: aiomotorengine.fields.uuid_field
.. py:module:: aiomotorengine.fields.list_field
.. py:module:: aiomotorengine.fields.embedded_document_field
.. py:module:: aiomotorengine.fields.reference_field
.. py:module:: aiomotorengine.fields.url_field
.. py:module:: aiomotorengine.fields.email_field
.. py:module:: aiomotorengine.fields.int_field
.. py:module:: aiomotorengine.fields.boolean_field
.. py:module:: aiomotorengine.fields.float_field
.. py:module:: aiomotorengine.fields.decimal_field
.. py:module:: aiomotorengine.fields.binary_field
.. py:module:: aiomotorengine.fields.json_field

AIOMotorEngine uses the concept of models to interact with MongoDB. To create a model we inherit from the `Document` class:

.. autoclass:: aiomotorengine.document.Document
  :noindex:

Let's say we need an article model with title, description and published_date:

.. testsetup:: modeling_1

    import asyncio 
    from aiomotorengine import connect

    io_loop = asyncio.get_event_loop()

    # you only need to keep track of the DB instance if you connect to multiple databases.
    connect("connecting-test", host="localhost", port=27017, io_loop=io_loop)

.. testcode:: modeling_1

    from aiomotorengine.document import Document
    from aiomotorengine.fields import StringField, DateTimeField

    class Article(Document):
        title = StringField(required=True)
        description = StringField(required=True)
        published_date = DateTimeField(auto_now_on_insert=True)

That allows us to create, update, query and remove articles with extreme ease:

.. testsetup:: modeling_2

    from uuid import uuid4
    import asyncio 
    from aiomotorengine import connect
    from aiomotorengine.document import Document
    from aiomotorengine.fields import StringField, DateTimeField

    io_loop = asyncio.get_event_loop()

    # you only need to keep track of the DB instance if you connect to multiple databases.
    connect("connecting-test", host="localhost", port=27017, io_loop=io_loop)

    class Article(Document):
        __collection__ = "ModelingArticles2"
        title = StringField(required=True)
        description = StringField(required=True)
        published_date = DateTimeField(auto_now_on_insert=True)

.. testcode:: modeling_2

    new_title = "Better Title %s" % uuid4()

    async def crud_article():
        article = await Article.objects.create(
            title="Some Article",
            description="This is an article that really matters."
        )
        
        article.title = new_title
        await article.save()
        
        articles = await Article.objects.filter(title=new_title).find_all()

        assert len(articles) == 1
        assert articles[0].title == new_title

        number_of_deleted_items = await articles[0].delete()

        assert number_of_deleted_items == 1

    io_loop.run_until_complete(crud_article())

.. testsetup:: modeling_fields

    from aiomotorengine import *

Base Field
----------

.. autoclass:: aiomotorengine.fields.base_field.BaseField

Available Fields
----------------

.. autoclass:: aiomotorengine.fields.string_field.StringField

.. autoclass:: aiomotorengine.fields.datetime_field.DateTimeField

.. autoclass:: aiomotorengine.fields.uuid_field.UUIDField

.. autoclass:: aiomotorengine.fields.url_field.URLField

.. autoclass:: aiomotorengine.fields.email_field.EmailField

.. autoclass:: aiomotorengine.fields.int_field.IntField

.. autoclass:: aiomotorengine.fields.boolean_field.BooleanField

.. autoclass:: aiomotorengine.fields.float_field.FloatField

.. autoclass:: aiomotorengine.fields.decimal_field.DecimalField

.. autoclass:: aiomotorengine.fields.binary_field.BinaryField

.. autoclass:: aiomotorengine.fields.json_field.JsonField

Multiple Value Fields
---------------------

.. autoclass:: aiomotorengine.fields.list_field.ListField

Embedding vs Referencing
------------------------

Embedding is very useful to improve the retrieval of data from MongoDB. When you have sub-documents that will always be used when retrieving a document (i.e.: comments in a post), it's useful to have them be embedded in the parent document.

On the other hand, if you need a connection to the current document that won't be used in the main use cases for that document, it's a good practice to use a Reference Field. MotorEngine will only load the referenced field if you explicitly ask it to, or if you set `__lazy__` to `False`.

.. autoclass:: aiomotorengine.fields.embedded_document_field.EmbeddedDocumentField

.. autoclass:: aiomotorengine.fields.reference_field.ReferenceField
