Connecting
==========

.. py:module:: aiomotorengine.connection

Simple Connection
-----------------

AIOMotorEngine supports connecting to the database using a myriad of options via the `connect` method.

.. autofunction:: aiomotorengine.connection.connect(db, host="localhost", port=27017, io_loop=io_loop)
  :noindex:

.. testsetup:: connecting_connecting

    import asyncio 

.. testcode:: connecting_connecting

    from aiomotorengine import connect

    # instantiate asyncio event loop 

    io_loop = asyncio.get_event_loop()

    # you only need to keep track of the DB instance if you connect to multiple databases.
    connect("connecting-test", host="localhost", port=27017, io_loop=io_loop)

Replica Sets
------------

.. autofunction:: aiomotorengine.connection.connect(db, host="localhost:27017,localhost:27018", replicaSet="myRs", io_loop=self.io_loop)
  :noindex:

.. testsetup:: connecting_replica_set

    import asyncio 

.. testcode:: connecting_replica_set

    from aiomotorengine import connect

    # get asyncio event loop 

    io_loop = asyncio.get_event_loop()
    connect("connecting-test", host="localhost:27017,localhost:27018", replicaSet="myRs", io_loop=io_loop)

The major difference here is that instead of passing a single `host`, you need to pass all the `host:port` entries, comma-separated in the `host` parameter.

You also need to specify the name of the Replica Set in the `replicaSet` parameter (the naming is not pythonic to conform to Motor and thus to pyMongo).

Multiple Databases
------------------

.. autofunction:: aiomotorengine.connection.connect(db, alias="db1", host="localhost", port=27017, io_loop=io_loop)
  :noindex:

Connecting to multiple databases is as simple as specifying a different alias to each connection.

Let's say you need to connect to an users and a posts databases:

.. testsetup:: connecting_multiple

    import asyncio 

    from aiomotorengine import Document, StringField

    class User(Document):
        first_name = StringField(required=True)
        last_name = StringField(required=True)

.. testcode:: connecting_multiple

    from aiomotorengine import connect

    # get asyncio event loop 

    io_loop = asyncio.get_event_loop()

    connect("posts", host="localhost", port=27017, io_loop=io_loop)                 # the posts database is the default
    connect("users", alias="users", host="localhost", port=27017, io_loop=io_loop)  # the users database uses an alias

    # now when querying for users we'll just specify the alias we want to use
    async def go():
        await User.objects.find_all(alias="users")
