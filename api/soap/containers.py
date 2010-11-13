from api.containers import ApiFunction
import inspect

class WebServiceFunction(ApiFunction):
    def gather_data(self):
        return {
            'name': self.function.__name__,
            'args': self.gather_data_function_args(),
            'return':self.out_type,
        }
    
    def gather_data_function_args(self):
        args = inspect.getargspec(self.function)[0]
        return [{'name': args[i+1], 'type': self.in_types[i]} for i in range(len(args[1:]))]
