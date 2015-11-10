Getting Started
===============

Installing
----------

Before installing AIOMotorEngine you should install the latest Motor asynchronous MongoDB driver::

    $ pip install https://github.com/mongodb/motor/archive/master.zip#egg=motor-0.5.dev0

AIOMotorEngine can be installed with pip, using::

    $ pip install https://github.com/ilex/aiomotorengine/archive/master.zip 

Connecting to a Database
------------------------

.. autofunction:: aiomotorengine.connection.connect

.. testsetup:: connecting

    import asyncio 
    from aiomotorengine import connect

.. testcode:: connecting

    # create an asyncio event loop 

    io_loop = asyncio.get_event_loop() 
    connect("test", host="localhost", port=27017, io_loop=io_loop)  # you only need to keep track of the
                                                                   # DB instance if you connect to multiple databases.

Modeling a Document
-------------------

.. autoclass:: aiomotorengine.document.Document

.. testsetup:: modeling

    import asyncio 
    from aiomotorengine import connect, Document, StringField, IntField

.. testcode:: modeling

    class User(Document):
        first_name = StringField(required=True)
        last_name = StringField(required=True)

    class Employee(User):
        employee_id = IntField(required=True)

Creating a new instance
-----------------------

.. automethod:: aiomotorengine.document.BaseDocument.save

.. testsetup:: creating_new_instance

    import asyncio 
    from aiomotorengine import connect, Document, StringField, IntField

    class User(Document):
        first_name = StringField(required=True)
        last_name = StringField(required=True)

    class Employee(User):
        __collection__ = "DocStringEmployee"
        employee_id = IntField(required=True)

    io_loop = asyncio.get_event_loop() 
    connect("test", host="localhost", port=27017, io_loop=io_loop)

.. testcode:: creating_new_instance

    async def create_employee():
        emp = Employee(first_name="Bernardo", last_name="Heynemann", employee_id=1532)
        emp = await emp.save()
        assert emp is not None
        assert emp.employee_id == 1532

    io_loop.run_until_complete(create_employee())

Updating an instance
--------------------

.. automethod:: aiomotorengine.document.BaseDocument.save

Updating an instance is as easy as changing a property and calling save again:

.. testsetup:: updating_instance

    import asyncio 
    from aiomotorengine import connect, Document, StringField, IntField

    class User(Document):
        first_name = StringField(required=True)
        last_name = StringField(required=True)

    class Employee(User):
        __collection__ = "DocStringEmployee"
        employee_id = IntField(required=True)

    io_loop = asyncio.get_event_loop()
    connect("test", host="localhost", port=27017, io_loop=io_loop)

.. testcode:: updating_instance

    async def update_employee():
        emp = Employee(first_name="Bernardo", last_name="Heynemann", employee_id=1532)
        await emp.save()
        emp.employee_id = 1534
        await emp.save()
        assert emp.employee_id == 1534

    io_loop.run_until_complete(update_employee())

Getting an instance
-------------------

.. automethod:: aiomotorengine.queryset.QuerySet.get

To get an object by id, you must specify the ObjectId that the instance got created with. This method takes a string as well and transforms it into a :mod:`bson.objectid.ObjectId <bson.objectid.ObjectId>`.

.. testsetup:: getting_instance

    import asyncio 
    from aiomotorengine import connect, Document, StringField, IntField

    class User(Document):
        first_name = StringField(required=True)
        last_name = StringField(required=True)

    class Employee(User):
        __collection__ = "DocStringEmployee"
        employee_id = IntField(required=True)

    io_loop = asyncio.get_event_loop() 
    connect("test", host="localhost", port=27017, io_loop=io_loop)

.. testcode:: getting_instance

    async def load_employee():
        emp = Employee(first_name="Bernardo", last_name="Heynemann", employee_id=1538)
        await emp.save()
        emp2 = await Employee.objects.get(emp._id)
        assert emp2 is not None
        assert emp2.employee_id == 1538

    io_loop.run_until_complete(load_employee())

Querying collections
--------------------

To query a collection in mongo, we use the `find_all` method.

.. automethod:: aiomotorengine.queryset.QuerySet.find_all

If you want to filter a collection, just chain calls to `filter`:

.. automethod:: aiomotorengine.queryset.QuerySet.filter

To limit a queryset to just return a maximum number of documents, use the `limit` method:

.. automethod:: aiomotorengine.queryset.QuerySet.limit

Ordering the results is achieved with the `order_by` method:

.. automethod:: aiomotorengine.queryset.QuerySet.order_by

All of these options can be combined to really tune how to get items:

.. testsetup:: filtering_instances

    import asyncio 
    from aiomotorengine import connect, Document, StringField, IntField

    class User(Document):
        first_name = StringField(required=True)
        last_name = StringField(required=True)

    class Employee(User):
        __collection__ = "DocStringEmployee"
        employee_id = IntField(required=True)

    io_loop = asyncio.get_event_loop()
    connect("test", host="localhost", port=27017, io_loop=io_loop)

.. testcode:: filtering_instances

    async def create_employee():
        emp = Employee(first_name="Bernardo", last_name="Heynemann", employee_id=1538)
        await emp.save()
        # return the first 10 employees ordered by last_name that joined after 2010
        employees = await Employee.objects \
              .limit(10) \
              .order_by("last_name") \
              .filter(last_name="Heynemann") \
              .find_all()

        assert len(employees) > 0
        assert employees[0].last_name == "Heynemann"

    io_loop.run_until_complete(create_employee())

Counting documents in collections
---------------------------------

.. automethod:: aiomotorengine.queryset.QuerySet.count

.. testsetup:: counting_instances

    import asyncio 
    from aiomotorengine import connect, Document, StringField, IntField

    class User(Document):
        first_name = StringField(required=True)
        last_name = StringField(required=True)

    class Employee(User):
        __collection__ = "DocStringCountInstancesEmployee"
        employee_id = IntField(required=True)

    io_loop = asyncio.get_event_loop()
    connect("test", host="localhost", port=27017, io_loop=io_loop)

.. testcode:: counting_instances

    async def count_employees():
        number_of_employees = await Employee.objects.count()
        assert number_of_employees == 0

    io_loop.run_until_complete(count_employees())
