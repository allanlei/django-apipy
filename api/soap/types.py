from decimal import Decimal
from api.types import BaseType, EnumerateType
from api.errors import TypeMismatchError

class WSBase(BaseType):
    class Meta(BaseType.Meta):
        ns = 'xs'
        namespace = 'http://www.w3.org/2001/XMLSchema'
        name = None
        complexType = False
    
    class Attributes(object):
        minOccurs = '0'
        nillable = 'true'
    
    @classmethod
    def attributes(cls):
        attrs = {}
        if hasattr(cls, 'Attributes'):
            for attr in dir(cls.Attributes):
                if not(attr.startswith('__') and attr.endswith('__')) and getattr(cls.Attributes, attr) is not None:
                    attrs[attr] = getattr(cls.Attributes, attr)
        return attrs
        

class List(WSBase, EnumerateType):
    class Meta(WSBase.Meta):
        python_type = list
        name = 'array'
        complexType = True
        
    class Attributes(WSBase.Attributes):
        maxOccurs = 'unbounded'
        
    @classmethod
    def serialize(cls, objs):
        if isinstance(objs, cls.Meta.python_type):
            ser = cls.Meta.python_type(cls.Meta.type.serialize(obj) for obj in objs)
            element = etree.Element('')
            return element
        raise TypeMismatchError('')
        
    @classmethod
    def deserialize(cls, obj):
        print 'deserialize'
        print obj, cls.Meta.types, cls.name
        if hasattr(cls, cls.Meta.pre_deserialize):
            obj = getattr(cls, cls.Meta.pre_deserialize)(obj)
        if cls.Meta.python_type is not None:
            try:
                obj = cls.Meta.python_type(obj)
            except:
                raise UnconvertibleTypeError
            if hasattr(cls, cls.Meta.post_deserialize):
                obj = getattr(cls, cls.Meta.post_deserialize)(obj)
            return obj
        raise NotImplementedError
        
        
        






class String(WSBase):
    class Meta(WSBase.Meta):
        python_type = str
        name = 'string'

class Integer(WSBase):
    class Meta(WSBase.Meta):
        python_type = int
        name = 'integer'

class Decimal(WSBase):
    class Meta(WSBase.Meta):
        python_type = Decimal
        name = 'decimal'
        
    @classmethod
    def pre_deserialize(cls, obj):
        return str(obj)
