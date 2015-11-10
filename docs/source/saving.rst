Saving instances
================

Creating new instances of a document
------------------------------------

The easiest way of creating a new instance of a document is using `Document.objects.create`. Alternatively, you can create a new instance and then call `save` on it.

.. automethod:: aiomotorengine.queryset.QuerySet.create

.. automethod:: aiomotorengine.document.Document.save

    .. testsetup:: saving_save

        import asyncio
        from aiomotorengine import *

        class User(Document):
            __collection__ = "UserSavingInstances"
            name = StringField()

        io_loop = asyncio.get_event_loop()
        connect("test", host="localhost", port=27017, io_loop=io_loop)

    .. testcode:: saving_save

        async def create_user():
            user = User(name="Bernardo")
            await user.save()
            assert user.name == "Bernardo"
        
        io_loop.run_until_complete(create_user())

Updating instances
------------------

To update an instance, just make the needed changes to an instance and then call `save`.

.. automethod:: aiomotorengine.document.Document.save

    .. testsetup:: saving_update

        import asyncio
        from aiomotorengine import *

        class User(Document):
            __collection__ = "UserUpdatingInstances"
            name = StringField()

        io_loop = asyncio.get_event_loop()
        connect("test", host="localhost", port=27017, io_loop=io_loop)

    .. testcode:: saving_update

        async def update_user():
            user = User(name="Bernardo")
            await user.save()
            user.name = "Heynemann"
            await user.save()
            assert user.name == "Heynemann"

        io_loop.run_until_complete(update_user())

Deleting instances
------------------

Deleting an instance can be easily accomplished by just calling `delete` on it:

.. automethod:: aiomotorengine.document.Document.delete

Sometimes, though, the requirements are to remove a few documents (or all of them) at a time. MotorEngine also supports deleting using filters in the document queryset.

.. automethod:: aiomotorengine.queryset.QuerySet.delete

Bulk inserting instances
------------------------

AIOMotorEngine supports bulk insertion of documents by calling the `bulk_insert` method of a queryset with an array of documents:

.. automethod:: aiomotorengine.queryset.QuerySet.bulk_insert(documents, alias=None)

.. testsetup:: saving_bulk

    import asyncio
    from aiomotorengine import *

    class User(Document):
        __collection__ = "UserBulkInsert"
        name = StringField()

    io_loop = asyncio.get_event_loop()
    connect("test", host="localhost", port=27017, io_loop=io_loop)

.. testcode:: saving_bulk

    async def create_users():
        users = [
            User(name="Bernardo"),
            User(name="Heynemann")
        ]
        users = await User.objects.bulk_insert(users)
        assert len(users) == 2
        assert users[0]._id
        assert users[1]._id

    io_loop.run_until_complete(create_users())
