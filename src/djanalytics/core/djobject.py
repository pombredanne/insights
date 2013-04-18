''' This is a generic interface to djanalytics. It presents views,
etc. as Python objects. 

This is prototype-grade code. 
'''

import requests
import urllib
import json

def http_rpc_helper(baseurl, function, headers = {}):
    def rpc_call(**kwargs):
        url = urllib.basejoin(baseurl, function)
        if kwargs:
            url = url+"?"+urllib.urlencode(kwargs)
        print url
        response = requests.get(url, headers = headers)
        if response.status_code == 200:
            return response.content
        if response.status_code == 404:
            raise AttributeError(function)
        error = "Error calling {func} {status}".format(func=function, status=response.status_code)
        raise Exception(error)
    rpc_call.__doc__ = "rpc call"
    return rpc_call

def local_call_helper(view_or_query, function):
    import djanalytics.core.views
    def rpc_call(**kwargs):
        return djanalytics.core.views.handle_request(view_or_query, function, **kwargs)
    return rpc_call

class embed():
    def __init__(self, view_or_query, baseurl = None, headers = {}):
        self.baseurl = baseurl
        if baseurl: 
            self.baseembedurl = baseurl+view_or_query
        self.view_or_query = view_or_query
        self.headers = headers

    def __getattr__(self, attr):
        ## Disallow internal. This is necessary both for analytics,
        ## and for Python. Otherwise, we have all sorts of __setattr__
        ## and similar overwritten
        if attr[0] == '_':
            return
        if self.baseurl:
            return http_rpc_helper(self.baseembedurl+"/", attr)
        else:
            return local_call_helper(self.view_or_query, attr)

    ## TODO: Use probe/schema to populate this
    def __dir__(self):
        results = []
        probeurl = self.baseurl+"probe/"+self.view_or_query
        classes = requests.get(probeurl, headers = self.headers).content.split('\n')
        for param_set in classes:
            items = requests.get(probeurl+"/"+param_set, headers = self.headers).content.split('\n')
            results = results + items
        return results

    def __repr__(self):
        return self.view_or_query+" object host: ["+self.baseurl+"]"
                                
class djobject():
    def __init__(self, baseurl = None, headers = {}):
        self.view = embed('view', baseurl = baseurl, headers = headers)
        self.query = embed('query', baseurl = baseurl, headers = headers)

if __name__ == "__main__":
    djo = djobject(baseurl = "http://127.0.0.1:8000/")
    print djo.query.djt_event_count()
    print djo.query.djt_user_event_count(user = "bob")
    print djo.query.__dir__()
