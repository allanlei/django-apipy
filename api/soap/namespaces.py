from api.utils import SearchableDict

WSDL = 'wsdl'
XS = 'xs'
XSI = 'xsi'
SOAP = 'soap'

SOAP_ENV = 'senv'
SOAP_ENC = 'senc'
SOAP_HTTP = 'soap_http'

NAMESPACES_1_1 = SearchableDict({
    XS: 'http://www.w3.org/2001/XMLSchema',
    XSI: 'http://www.w3.org/2001/XMLSchema-instance',
    WSDL: 'http://schemas.xmlsoap.org/wsdl/',

    SOAP: 'http://schemas.xmlsoap.org/wsdl/soap/',
    SOAP_ENV: 'http://schemas.xmlsoap.org/soap/envelope/',
    SOAP_ENC: 'http://schemas.xmlsoap.org/soap/encoding/',
    SOAP_HTTP: 'http://schemas.xmlsoap.org/soap/http',
    
#    'plink': 'http://schemas.xmlsoap.org/ws/2003/05/partner-link/',
#    'wsa': 'http://schemas.xmlsoap.org/ws/2003/03/addressing',
#    'xop': 'http://www.w3.org/2004/08/xop/include',
#    's12env': 'http://www.w3.org/2003/05/soap-envelope/',
#    's12enc': 'http://www.w3.org/2003/05/soap-encoding/',
})

NAMESPACES_1_2 = SearchableDict({
    XS: 'http://www.w3.org/2001/XMLSchema',
    XSI: 'http://www.w3.org/2001/XMLSchema-instance',
    WSDL: 'http://schemas.xmlsoap.org/wsdl/',

    SOAP: 'http://schemas.xmlsoap.org/wsdl/soap/',
    SOAP_ENV: 'http://www.w3.org/2003/05/soap-envelope/',
    SOAP_ENC: 'http://www.w3.org/2003/05/soap-encoding/',
    SOAP_HTTP: 'http://schemas.xmlsoap.org/soap/http',
})

DEFAULT_NAMESPACES = NAMESPACES_1_1
