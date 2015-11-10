AIOMotorEngine MongoDB Asyncio ORM
==================================

.. py:module:: aiomotorengine

`AIOMotorEngine`_ is a port (for asyncio's event loop) of the `MotorEngine`_ which is port of the `MongoEngine`_.
The most part of the code is based on `MotorEngine`_. A few classes and functions were rewritten using async and await for asynchronous code (this syntax was introduced in python 3.5). All tests are rewritten too and seem to pass.
AIOMotorEngine does not require Tornado but Motor still does.

Supported Versions
------------------

`AIOMotorEngine`_ is compatible and tested against python 3.5.

`AIOMotorEngine`_ requires MongoDB 2.2+ due to usage of the `Aggregation Pipeline`_.

The tests of compatibility are always run against the current stable version of `MongoEngine`_.

Defining Documents
------------------

Defining a new document is as easy as:

.. code-block:: python

    from aiomotorengine import Document, StringField

    class User(Document):
        __collection__ = "users"  # optional. if no collection is specified, class name is used.

        first_name = StringField(required=True)
        last_name = StringField(required=True)

        @property
        def full_name(self):
            return "%s, %s" % (self.last_name, self.first_name)

`AIOMotorEngine`_ comes baked in with the same fields as `MotorEngine`_.

Example
-------

Let's see how to use `AIOMotorEngine`_:

.. code-block:: python

    import asyncio
    import pymongo
    from aiomotorengine import connect, Document, StringField, IntField


    class User(Document):
        __collection__ = 'users'

        name = StringField(required=True, unique=True)
        age = IntField()

        def __repr__(self):
            return '<User: {0}({1})>'.format(self.name, self.age)


    async def create():
        user = await User.objects.create(name='Python', age=13)
        print(user)
        user2 = User(name='Linux', age=20)
        await user2.save()
        print("_id of user2 is {0}".format(user2._id))

    async def query():
        cursor = User.objects.filter(age__gt=10)
        cursor.order_by(User.name, pymongo.DESCENDING)
        cursor.limit(2)
        users = await cursor.find_all()
        print(users)

    loop = asyncio.get_event_loop()
    connect('xxx', io_loop=loop)
    loop.run_until_complete(create())
    loop.run_until_complete(query())   
    
Contents
--------

.. toctree::
  :maxdepth: 2

  getting-started
  connecting
  modeling
  saving
  getting-and-querying


.. _AIOMotorEngine: http://github.com/ilex/aiomotorengine/
.. _MotorEngine: http://motorengine.readthedocs.org/en/latest/
.. _MongoEngine: http://docs.mongoengine.org/en/latest/
.. _Motor: http://motor.readthedocs.org/en/stable/
.. _Aggregation Pipeline: http://docs.mongodb.org/manual/reference/method/db.collection.aggregate/#db.collection.aggregate
