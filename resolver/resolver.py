
import json

from twisted.internet import reactor
from twisted.web import server, resource
from twisted.application import service
from twisted.python import log

from geoservices import factories

class ResolverService(service.Service):
    def __init__(self, host, portNum, geo_engine):
        self._host    = host
        self._portNum = portNum
        self._geo_engine = geo_engine
        
    def startService(self):
        self._port = reactor.listenTCP(self._portNum, server.Site(_EntryPoint(self._geo_engine)), interface=self._host)

    def stopService(self):
        return self._port.stopListening()

class _EntryPoint(resource.Resource):
    
    def __init__(self, geo_engine):
        resource.Resource.__init__(self)
        self._geo_engine = geo_engine
        
    def getChild(self, name, request):
        return _GeoPage(name, self._geo_engine)

class _GeoPage(resource.Resource):
    isLeaf = True
    
    def __init__(self, ip_addr, geo_engine):
        resource.Resource.__init__(self)
        self.ip_addr = ip_addr
        self._geo_engine = geo_engine
    
    def render_GET(self, request):
        data = self._geo_engine.resolveLocation(self.ip_addr)
        return json.dumps(data)

def makeService(config):
    
    geo_resolver_type = config['resolver'];
    geo_file          = config['file'];
    
    host              = config['host'];
    port              = config['port'];
    
    factory = factories.LocationResolverFactory();
    
    resolver_engine = factory.getLocationResolver(geo_resolver_type);
    resolver_engine.setAddrFile(geo_file);
    
    service = ResolverService(host, port, resolver_engine)
    
    return service

