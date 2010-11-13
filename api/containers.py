import inspect

class ApiFunction(object):
    def __init__(self, function, in_types, out_type, function_args_offset=1):
        self.function = function
        self.function_name = self.function.__name__
        self.function_args = inspect.getargspec(self.function)[0][function_args_offset:]
        self.in_types = in_types
        self.out_type = out_type
    
    @property
    def outtype(self):
        return self.out_type
    
    def get_descriptor(self):
        return tuple([self.function_name] + self.function_args)    
        
    def dispatch(self, *args, **kwargs):
        ds_kwargs = self.deserialize(kwargs)
        result = self.run(*args, **ds_kwargs)
        return self.serialize(result)
    
    def run(self, *args, **kwargs):
        return self.function(*args, **kwargs)
    
    def serialize(self, result):
        return self.out_type.serialize(result)
    
    def deserialize(self, kwargs):
        for i in range(len(kwargs.keys())):
            key = kwargs.keys()[i]
            value = kwargs[key]
            converted = self.in_types[i].deserialize(value)
            kwargs[key] = converted
        return kwargs
