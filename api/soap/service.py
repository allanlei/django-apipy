from api.service import ApiService
from api.soap.message import WebServiceDocument
from api.errors import ValidationError
from api.utils import dict_search

from lxml import etree
from lxml.builder import ElementMaker
from django.http import HttpResponse

from namespaces import DEFAULT_NAMESPACES, SOAP_ENV, XSI
from containers import WebServiceFunction


class WebService(ApiService):
    class Meta(ApiService):
        wrapper = WebServiceFunction
        
    def __init__(self, target_ns=None, namespaces=DEFAULT_NAMESPACES, ns_name=None, *args, **kwargs):
        super(WebService, self).__init__(*args, **kwargs)
        self.target_ns = target_ns
        self.namespaces = namespaces
        self.add_tns_entry(ns_name, self.target_ns)
        
        self.wsdl = WebServiceDocument(
            namespaces=self.namespaces, 
            target_ns=self.target_ns,
            service_name=self.service_name, 
            service_url=self.service_url
        )
    def add_tns_entry(self, tns_name, tns_namespace):
            counter = None
            tns_name = '%s%s' % (tns_name or 'ns', counter or '')
            while self.namespaces.search(tns_name) not in [tns_namespace, None]:
                counter = (counter or 0) + 1
                tns_name = '%s%s' % (tns_name or 'ns', counter or '')
            self.namespaces.update({tns_name: tns_namespace})
            
    def add_method_hook(self, fn):
        self.wsdl.functions = [fn for fn in self.functions.values()]
        
    def generate_wsdl(self, request):
        return HttpResponse(str(self.wsdl), content_type='text/xml')
    
    def get_function(self, function):
        name = function.tag.replace('{%s}' % function.nsmap[function.prefix], '')
        arg_elements = function.xpath('%s:*' % self.namespaces.search(value=self.target_ns), namespaces=self.namespaces)
        args = dict([(arg.tag.replace('{%s}' % arg.nsmap[arg.prefix], ''), arg.text) for arg in arg_elements])
        return super(WebService, self).get_function(name, **args)
    
    def validate_request(self, request, accepted=['POST']):
        return request.method in accepted
    
    def parse_request(self, request):
        message = etree.fromstring(request.raw_post_data)
        header = message.xpath('%s:Header' % SOAP_ENV, namespaces=self.namespaces)[0]
        body = message.xpath('%s:Body' % SOAP_ENV, namespaces=self.namespaces)[0]
        
        if header is None or body is None:
            raise ValidationError('Not a SOAP request')
        if len(header) == 0 and len(body) == 0:
            raise ValidationError('Empty SOAP envelope')
        if len(body) > 1:
            raise ValidationError('Too many requested functions')
        
        functions = body.xpath('%s:*' % self.namespaces.search(value=self.target_ns), namespaces=self.namespaces)
        return functions[0]
    
    def process(self, request, parsed_data):
        function = parsed_data
        wsf, args = self.get_function(function)
        result = wsf.dispatch(request, **args)
        return result, wsf

    def package(self, request, response, function=None):
        E = ElementMaker(namespace=self.namespaces.search(SOAP_ENV), nsmap=self.namespaces)
        wsf = function
        
        envelope = E.Envelope(
            E.Header(), 
            E.Body(
                E('{%s}%sResponse' % (self.target_ns, wsf.function_name),
                
                    E('{%s}%sResult' % (self.target_ns, wsf.function_name), 
                        response, 
                        **{'{%s}type' % self.namespaces.search(XSI): '%s:%s' % (self.namespaces.search(value=wsf.outtype.Meta.namespace), wsf.outtype.Meta.name)}
                    )
                    
                    
                )
            )
        )
        return HttpResponse(etree.tostring(envelope), content_type='text/xml')
