# -*- coding: utf-8 -*-

import struct, zlib
from errors import *

class MemCacheBinaryProtocol:

    HEADER = '!BBHBBHLLQ'
    HEADER_SIZE = 24
    FLAGS_COMPRESSED = 1

    def __init__(self, compress, compression_threshold):
        '''
        Inititalize a MemCache binary protocol helper instance
        '''
        self.compress = compress
        self.compression_threshold = compression_threshold
        
    def get_command(self, key):
        '''
        Build the binary structure that represents a GET command
        '''
        ln = len(key)
        return struct.pack(MemCacheBinaryProtocol.HEADER+'%ds'%(ln), 0x80, 0x00, ln, 0, 0, 0, ln, 0, 0, key)

    def set_command(self, key, value, ttl, flags):
        '''
        Build the binary structure that represents a SET command
        '''
        lnk = len(key)
        lnv = len(value)
        return struct.pack(MemCacheBinaryProtocol.HEADER+'LL%ds%ds'%(lnk, lnv), 0x80, 0x01, lnk, 8, 0, 0, lnk + lnv + 8, 0, 0, flags, ttl, key, value)

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
                    #log key not found. message = content
                    raise MemCacheKeyNotFoundException(key, server)
                    
                if status == MemCacheServerDisconnectionException.STATUS_CODE:
                    # log server disconnected
                    raise MemCacheServerDisconnectionException(server)
                    
                raise MemCacheUnknownException(status, content)
            
            # Return length of following body chunk to read
            return bodylen
        except Exception as e:
            raise 

    def parse_response(self, bodylen, content):
        '''
        Parse a response
        '''
        flags, value = struct.unpack('!L%ds' % (bodylen-4,), content)
        if flags & MemCacheBinaryProtocol.FLAGS_COMPRESSED:
            value = zlib.decompress(value)
            
        return value

    def prepare_value(self, value):
        '''
        Prepare a value to be written to MemCache
        '''
        flags = 0
        if self.compress and (len(value) > self.compression_threshold):
            value = zlib.compress(value)
            flags |= MemCacheBinaryProtocol.FLAGS_COMPRESSED
            
        return flags, value

