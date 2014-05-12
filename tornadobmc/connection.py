# -*- coding: utf-8 -*-

import socket, errno, zlib, time
from datetime import timedelta
from urllib import splitport
from tornado.iostream import IOStream
from tornado.gen import Task, Return, coroutine
from timeout import WithTimeout
from protocol import *
from errors import *

class Connection:

    FLAGS_COMPRESSED = 1

    def __init__(self, address, timeout, compress, compression_threshold, server_ttl):
        '''
        Initialize a new MemCache connection
        '''
        self.timeout = timeout
        self.compress = compress
        self.server_ttl = server_ttl
        self.compression_threshold = compression_threshold
        self.connection = None
        self.connection_time = None
        self.protocol = MemCacheBinaryProtocol()

        # Parse and save the remote address as a tuple
        host, port = splitport(address)
        self.address = (host, 11211 if port is None else port)

    def connect(self, should_raise=True):
        '''
        Open a connection to the MemCache server, if one is not already open
        '''
        if self.connection is None:
            try:
                # Initialize socket and connect to remote MemCache server
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(self.address)

                # Wrap socket in Tornado's async IO Stream
                self.connection = IOStream(sock)
                self.connection_time = time.time()
            except Exception as e:
                self.connection = None
                self.connection_time = None
                if should_raise:
                    if e.errno == errno.ETIMEDOUT:
                        raise MemCacheTimeoutException(str(self.address), e.strerror)
                    else:
                        raise MemCacheConnectionErrorException(str(self.address), e)
                return False
        elif time.time() - self.connection_time > self.server_ttl:
                # Close current connection
                self.disconnect()
                # Establish a new one
                return self.connect(should_raise)
            
        return True

    def disconnect(self):
        '''
        Close the current connection
        '''
        try:
            if self.connection is not None:
                self.connection.close()
        finally:
            self.connection = None
            self.connection_time = None

    @coroutine
    def get(self, key):
        '''
        Get a value from MemCache
        '''
        # Send GET command
        cmd = self.protocol.get_command(key)
        yield self._send(cmd)
        
        # Get response
        res = yield self._get_response(key)
        raise Return(res)

    @coroutine
    def set(self, key, value, ttl=0):
        '''
        Set a value into MemCache
        '''
        # Prepare value to SET
        flags = 0
        if self.compress and (len(value) > self.compression_threshold):
            value = zlib.compress(value)
            flags |= Connection.FLAGS_COMPRESSED
        value = self.protocol.prepare_value(value, flags)
        
        # Send SET command
        cmd = self.protocol.set_command(key, value, ttl, flags)
        yield self._send(cmd)
    
        # Get response
        yield self._get_response(key)

    @coroutine
    def _get_response(self, key):
        '''
        Parse and return the response from MemCache
        '''
        # Read header from stream
        header = yield self._recv(MemCacheBinaryProtocol.HEADER_SIZE)
        if header is not None:
            # Get number of bytes to read for response chunk
            bodylen = self.protocol.parse_response_header(header, key, str(self.address))
            if bodylen:
                # Read response chunk
                binary_content = yield self._recv(bodylen)
                # Parse chunk into a meaningful value
                flags, content = self.protocol.parse_response(bodylen, binary_content)
                # Decompress it, if needed
                if flags & Connection.FLAGS_COMPRESSED:
                    content = zlib.decompress(content)

                raise Return(content)
        else:
            raise MemCacheInvalidResponseException()
        
    @coroutine
    def _send(self, data):
        '''
        Send data asynchronously over our open connection
        '''
        if not self.connect():
            return

        res = yield Task(self.connection.write, data)
        raise Return(res)

    @coroutine
    def _recv(self, num_bytes):
        '''
        Read from socket up to the requested number of bytes, with timeout
        '''
        if not self.connect():
            return
        
        # Create asynchornous task for reading
        task = Task(self.connection.read_bytes, num_bytes)

        # yield the task to obtain it's result (or timeout!)
        res = yield WithTimeout(timedelta(seconds=self.timeout), task, exception=MemCacheTimeoutException(str(self.address)))

        raise Return(res)

