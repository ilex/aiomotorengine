__version__ = '0.9.0'

try:
    from pymongo import ASCENDING, DESCENDING  # NOQA

    from aiomotorengine.connection import connect, disconnect  # NOQA
    from aiomotorengine.document import Document  # NOQA

    from aiomotorengine.fields import (  # NOQA
        BaseField, StringField, BooleanField, DateTimeField,
        UUIDField, ListField, EmbeddedDocumentField, ReferenceField, URLField,
        EmailField, IntField, FloatField, DecimalField, BinaryField,
        JsonField, PasswordField
    )

    from aiomotorengine.aggregation.base import Aggregation  # NOQA
    from aiomotorengine.query_builder.node import Q, QNot  # NOQA

except ImportError:  # NOQA
    pass  # likely setup.py trying to import version
