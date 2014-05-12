# -*- coding: utf-8 -*-

from connection import Connection
from tornado.gen import Return, coroutine
from errors import *

class Client:

    def __init__(self, server_list, compress=True, compression_threshold=128, timeout=0.01, server_ttl=3600):
        '''
        Initialize a MemCache client for the given servers.
        
        @param server_list Array of servers to connect to
        @param compress Should data be compressed, if it exceeds the compression threshold?
        @param compression_threshold Minimum number of bytes that trigger data compression
        @param timeout Timeout (in seconds) to wait for MemCache response
        @param server_ttl Time To Live for each server. After this time, it's connection will be closed and reopened when necessary
        '''
        self.connections = [Connection(server, timeout, compress, compression_threshold, server_ttl) for server in (server_list if isinstance(server_list, list) else [server_list])]
        self.hash_function = Client._calc_hash_index

    def disconnect(self):
        '''
        Disconnect all open MemCache connections
        '''
        for connection in self.connections:
            connection.disconnect()

    def set_server_ttl(self, server_ttl):
        '''
        Permit modifying the server connection ttl value
        '''
        for connection in self.connections:
            connection.server_ttl = server_ttl
    
    def set_timeout(self, new_timeout):
        '''
        Permit modifying the initial timeout value
        '''
        for connection in self.connections:
            connection.timeout = new_timeout
    
    def set_compression_threshold(self, compression_threshold):
        '''
        Permit modifying the initial compression threshold
        '''
        for connection in self.connections:
            connection.compression_threshold = compression_threshold
    
    def set_hash_function(self, function):
        '''
        Define a different hash function to be used when selecting a MemCache server
        '''
        self.hash_function = function

    @coroutine
    def get(self, key):
        '''
        Retrieve a key from MemCache
        '''
        if key is None:
            raise Return((None, None))
            
        server_index = self.hash_function(key, len(self.connections))
        
        # Get result from MemCache
        value = yield self.connections[server_index].get(key)
        
        # Return the value and the index of the server used for reading
        raise Return((value, server_index))
        
    @coroutine
    def set(self, key, value, ttl=0):
        '''
        Set a key into one of the MemCache servers
        '''
        if key is None or value is None:
            raise Return((False, None))

        server_index = self.hash_function(key, len(self.connections))
        yield self.connections[server_index].set(key, value, ttl)
        
        # Return which server was used
        raise Return(server_index)

    @staticmethod
    def _calc_hash_index(key, server_count):
        '''
        Calculate a hash over the given key in order to determine which server should be used.
        This is the default function and will be used if none other is specified.
        '''
        if server_count <= 1:
            return 0
            
        _sum = sum([ord(c) for c in key])
        return _sum % server_count

