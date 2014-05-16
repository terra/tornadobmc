# -*- coding: utf-8 -*-

import struct
from errors import *

class MemCacheBinaryProtocol:

    HEADER = '!BBHBBHLLQ'
    HEADER_SIZE = 24

    def get_command(self, key):
        '''
        Build the binary structure that represents a GET command
        '''
        ln = len(key)
        return struct.pack(MemCacheBinaryProtocol.HEADER+'%ds'%ln, 0x80, 0x00, ln, 0, 0, 0, ln, 0, 0, key)

    def set_command(self, key, value, ttl, flags, cas):
        '''
        Build the binary structure that represents a SET command
        '''
        lnk = len(key)
        lnv = len(value)
        return struct.pack(MemCacheBinaryProtocol.HEADER+'LL%ds%ds'%(lnk, lnv), 0x80, 0x01, lnk, 8, 0, 0, lnk + lnv + 8, 0, cas, flags, ttl, key, value)

    def parse_response_header(self, header, key, server):
        '''
        Parse the given response header and return it's most important parts
        '''
        try:
            # Unpack/parse response header
            (magic, opcode, keylen, extlen, datatype, status, bodylen, opaque, cas) = struct.unpack(MemCacheBinaryProtocol.HEADER, header)
            
            # Validate header magic token
            if magic != MemCacheInvalidResponseException.RESPONSE_CODE:
                raise MemCacheInvalidResponseException(magic)
            
            # Check for errors based on return status code
            if status != 0x00: # success
                if status == MemCacheKeyNotFoundException.STATUS_CODE:
                    # log key not found.
                    raise MemCacheKeyNotFoundException(key, server, bodylen)
                    
                if status == MemCacheCASException.STATUS_CODE:
                    # CAS mismtach
                    raise MemCacheCASException(key, server, bodylen)
                    
                if status == MemCacheServerDisconnectionException.STATUS_CODE:
                    # log server disconnected
                    raise MemCacheServerDisconnectionException(server)
                
                raise MemCacheUnknownException(status)
            
            # Return length of following body chunk to read
            return bodylen, cas
        except Exception as e:
            raise 

    def parse_response(self, bodylen, content):
        '''
        Parse a response.
        For the binary protocol, there's nothing more we need to do here!
        '''
        flags, value = struct.unpack('!L%ds' % (bodylen-4,), content)
        return flags, value

    def prepare_value(self, value, flags):
        '''
        Prepare a value to be written to MemCache.
        Default implementation for the Binary protocol does nothing!
        '''
        return value

