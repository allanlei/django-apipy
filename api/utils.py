import inspect
from django.core import urlresolvers

def dict_search(d, key=None, value=None):
    if key is not None:
        return d.get(key, None)
    elif value is not None:
        di = [key for key, val in d.iteritems() if val == value]
        return di[0] if len(di) else None
    return None


class SearchableDict(dict):        
    def search(self, key=None, value=None):
        return dict_search(self, key, value)


