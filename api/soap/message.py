from lxml.builder import ElementMaker
from lxml import etree
from namespaces import XS, WSDL, SOAP, SOAP_HTTP

class WebServiceDocument(object):
    def __init__(self, service_name=None, service_url=None, target_ns=None, namespaces=None, functions=[]):
        self.tns = target_ns
        self.namespaces = namespaces
        self._functions = functions
        self.service_name = service_name
        self.service_url = service_url
        self.wsdl = None
    
    @property
    def functions(self):
        return self._functions
    
    @functions.setter
    def functions(self, value):
        self._functions = value
        self.generate()
        
    @functions.deleter
    def functions(self):
        del self._functions
        self.generate()
        
    def generate(self):
        ns = self.namespaces
        tns = ns.search(value=self.tns)
        xs_ns = ns.search(XS)
        wsdl_ns = ns.search(WSDL)
        soap_ns = ns.search(SOAP)
        fnd = [fn.gather_data() for fn in self.functions]
        
        complexTypes = []
        for fn in fnd:
            for arg in (fn['args']):
                if arg['type'].Meta.complexType:
                    complexTypes.append(arg['type'])
            if fn['return'].Meta.complexType:
                complexTypes.append(fn['return'])
        
        E = ElementMaker(namespace=self.tns, nsmap=ns)
        
        
        self.wsdl = E('{%s}definitions' % wsdl_ns, 
            E('{%s}types' % wsdl_ns,
                E('{%s}schema' % xs_ns, targetNamespace=self.tns, elementFormDefault='qualified',
                    *(
                        [E('{%s}element' % xs_ns, name=fn['name'], type='%s:%s' % (tns, fn['name'])) for fn in fnd] + 
                        [E('{%s}element' % xs_ns, name='%sResponse' % fn['name'], type='%s:%sResponse' % (tns, fn['name'])) for fn in fnd] + 
                        [E('{%s}element' % xs_ns, name=ct.Meta.name, type='%s:%s' % (tns, ct.Meta.name)) for ct in complexTypes] +
                        [E('{%s}complexType' % xs_ns, 
                            E('{%s}sequence' % xs_ns, 
                                *[E('{%s}element' % xs_ns, 
                                    name=arg['name'], 
                                    type='%s:%s' % (ns.search(value=arg['type'].Meta.namespace), arg['type'].Meta.name), 
                                    **arg['type'].attributes()
                                ) for arg in fn['args']]
                            ), 
                            name=fn['name']
                        ) for fn in fnd] + 
                        [E('{%s}complexType' % xs_ns,
                            E('{%s}sequence' % xs_ns, 
                                E('{%s}element' % xs_ns, 
                                    name='%sResult' % fn['name'], 
                                    type='%s:%s' % (ns.search(value=fn['return'].Meta.namespace), fn['return'].Meta.name), 
                                    **(fn['return'].Meta.type if hasattr(fn['return'].Meta, 'type') else fn['return']).attributes()
                                )
                            ),
                            name='%sResponse' % fn['name']
                        ) for fn in fnd] +
                        [E('{%s}complexType' % xs_ns,
                            E('{%s}sequence' % xs_ns, 
                                E('{%s}element' % xs_ns, 
                                    name=ct.Meta.type.Meta.name, 
                                    type='%s:%s' % (ns.search(value=ct.Meta.type.Meta.namespace), ct.Meta.type.Meta.name), 
                                    **ct.attributes()
                                )
                            ),
                            name=ct.Meta.name 
                        ) for ct in complexTypes]
                        
                        
                        
                        
                    )
                )
            ), name=self.service_name, targetNamespace=self.tns,
            *(
                [E('{%s}message' % wsdl_ns,
                    E('{%s}part' % wsdl_ns, name=fn['name'], element='%s:%s' % (tns, fn['name'])),
                    name=fn['name']
                ) for fn in fnd] + 
                [E('{%s}message' % wsdl_ns, 
                    E('{%s}part' % wsdl_ns, name='%sResponse' % fn['name'], element='%s:%sResponse' % (tns, fn['name'])),
                    name='%sResponse' % fn['name']
                ) for fn in fnd] + 
                [E('{%s}service' % wsdl_ns,
                    E('{%s}port' % wsdl_ns, 
                        E('{%s}address' % soap_ns, location=self.service_url),
                        name=self.service_name, binding='%s:%s' % (tns, self.service_name)
                    ),
                    name=self.service_name
                )] +
                [E('{%s}portType' % wsdl_ns, name=self.service_name,
                    *[E('{%s}operation' % wsdl_ns, 
                        E('{%s}input' % wsdl_ns, name=fn['name'], message='%s:%s' % (tns, fn['name'])),
                        E('{%s}output' % wsdl_ns, name='%sResponse' % fn['name'], message='%s:%sResponse' % (tns, fn['name'])),
                        name=fn['name'], parameterOrder=fn['name']
                    ) for fn in fnd]
                )] +
                [E('{%s}binding' % wsdl_ns, 
                    E('{%s}binding' % soap_ns, style='document', transport=ns.search(SOAP_HTTP)),
                    name=self.service_name, type='%s:%s' % (tns, self.service_name),
                    *[E('{%s}operation' % wsdl_ns, 
                        E('{%s}operation' % soap_ns, soapAction=fn['name'], style='document'),
                        E('{%s}input' % wsdl_ns, 
                            E('{%s}body' % soap_ns, use='literal'),
                            name=fn['name']
                        ),
                        E('{%s}output' % wsdl_ns,
                            E('{%s}body' % soap_ns, use='literal'),
                            name='%sResponse' % fn['name']
                        ),
                        name=fn['name']
                    ) for fn in fnd]
                )]
            )
        )
        
    def __str__(self):
        return etree.tostring(self.wsdl, xml_declaration=True, encoding='UTF-8')
