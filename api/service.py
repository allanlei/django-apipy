from containers import ApiFunction
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseServerError
from errors import ValidationError, ParsingError, PackagingError

class ApiService(object):
    class Meta:
        wrapper = ApiFunction
        
    def __init__(self, service_name=None, service_url=None, service_url_reverse=None):
        self.service_name = service_name or self.__class__.__name__
        self.service_url = service_url
        self.functions = {}
        
    def add_method(self, *in_types, **kwargs):
        returns = kwargs['returns']
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **fn_kwargs)
            function = self.__class__.Meta.wrapper(function=func, in_types=in_types, out_type=returns)
            self.functions[function.get_descriptor()] = function
            self.add_method_hook(function)
            return wrapper
        return decorator
    
    def add_method_hook(self, fn):
        pass
    
    def get_function(self, fn_name, **kwargs):
        key = tuple([fn_name] + kwargs.keys())
        return (self.functions[key], kwargs) if key in self.functions else None
    
    def update_service_url(self, url=None):
        if url is not None:
            self.service_url = url
        elif self.service_url is None and service_url_reverse is not None:
            self.service_url = reverse(self.service_url_reverse)
            self.service_url_reverse = None
            
    def serve(self, request):
        self.pre_serve(request)
        
        if self.validate_request(request) is False:
            return HttpResponseNotAllowed()
            
        try:
            parsed_data = self.parse_request(request)
        except ValidationError, ve:
            return HttpResponseBadRequest(ve)
            
        if self.validate_data(request, parsed_data) is False:
            return HttpResponseBadRequest()
        
        try:
            response, function = self.process(request, parsed_data)
            out = self.package(request, response, function)
        except Exception, err:
            print err.__class__.__name__
            return HttpResponseServerError()
        
        if self.validate_response(request, out) is False:
            return HttpResponseServerError()
            
        self.post_serve(request, out)
        return out
    
    def pre_serve(self, request):
        self.update_service_url()
    
    def validate_request(self, request):
        pass
    
    def parse_request(self, request):
        raise NotImplementedError
    
    def validate_data(self, request, cleaned_data):
        pass
    
    def process(self, request, parsed_data):
        raise NotImplementedError

    def package(self, request, response):
        return response
    
    def validate_response(self, request, out):
        if isinstance(out, HttpResponse):
            return out
        raise ValidationError()
    
    def post_serve(self, request, response):
        pass
