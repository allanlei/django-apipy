class BaseType(object):
    class Meta(object):
        python_type = None
        pre_deserialize = 'pre_deserialize'
        post_deserialize = 'post_deserialize'
    
    @classmethod
    def serialize(cls, obj):
        return str(obj)
    
    @classmethod
    def deserialize(cls, obj):
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
    
    @classmethod
    def tostring(cls, obj):
        return str(cls.deserialize(obj))

class EnumerateType(BaseType):
    class EnumerateMeta(object):
        type = None
        
    def __new__(cls, base_type):
        meta = type(cls.Meta.__name__, (cls.Meta, cls.EnumerateMeta), dict(name='%s%s' % (base_type.Meta.name, cls.Meta.name.capitalize())))
        meta.type = base_type
        new_List = type(cls.__name__, (cls, ), dict(Meta=meta))
        return new_List
        
class UnconvertibleTypeError(Exception):
    pass
