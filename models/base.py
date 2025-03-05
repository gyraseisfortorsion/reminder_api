import uuid
import datetime

from sqlalchemy import TIMESTAMP, Column, String, text, CLOB
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.dialects.postgresql import UUID
from abc import abstractmethod

from core import Base

"""
    This class is abstract entity class,
    which provides following columns to all inherited entities:
    - **id** : UUID - clustered index of table
    - **created_at**: datetime - Creation timestamp of entity
    - **updated_at**: datetime - Update timestamp of entity
"""


class Cloneable():
    
    @abstractmethod
    def clone(self, **attr):
        new_obj = self.__class__()
                
        new_obj.__dict__.update(attr)
        new_obj.id = str(uuid.uuid4())
        new_obj.created_at = datetime.datetime.now()
        new_obj.updated_at = datetime.datetime.now()
        
        return new_obj


class Model(Base, Cloneable):

    __abstract__ = True

    id = Column(UUID, primary_key=True,
                nullable=False, default=lambda: str(uuid.uuid4()))

    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))





