# -*- coding: utf-8 -*-

class MemCacheExceptionBase(Exception):
    pass    

class MemCacheUnknownException(MemCacheExceptionBase):

    def __init__(self, code, message = ''):
        '''
        Initialize an Unknown error exception
        '''
        self.code = code
        self.message = 'Unknown error. Code [{0}] Message [{1}]'.format(code, message)
        super(MemCacheUnknownException, self).__init__(self.message)

class MemCacheInvalidResponseException(MemCacheExceptionBase):

    RESPONSE_CODE = 0x81
    
    def __init__(self, magic=None):
        '''
        Initialize an Invalid response exception
        '''
        self.magic = magic
        if magic:
            self.message = 'Invalid response header. Expected magic [{0}] got [{1}]'.format(self.RESPONSE_CODE, magic)
        else:
            self.message = 'Invalid response header'
        super(MemCacheInvalidResponseException, self).__init__(self.message)
    
class MemCacheKeyNotFoundException(MemCacheExceptionBase, KeyError):

    STATUS_CODE = 0x01
    
    def __init__(self, key, server, bodylen=None):
        '''
        Initialize a Key not found exception
        '''
        self.key = key
        self.server = server
        self.bodylen = bodylen
        self.message = 'Key [{0}] not found in MemCache server [{1}]'.format(key, server)
        super(MemCacheKeyNotFoundException, self).__init__(self.message)

class MemCacheCASException(MemCacheExceptionBase, KeyError):

    STATUS_CODE = 0x02
    
    def __init__(self, key, server, bodylen=None):
        '''
        Initialize a CAS set exception.
        This is actually a Key already exists exception, but in the CAS command context it means
        that the operation could not complete due to CAS unique value mismatch.
        '''
        self.key = key
        self.server = server
        self.bodylen = bodylen
        self.message = 'Unable to store value for [{0}] in MemCache server [{1}]. CAS mismatch.'.format(key, server)
        super(MemCacheCASException, self).__init__(self.message)

class MemCacheServerDisconnectionException(MemCacheExceptionBase):

    STATUS_CODE = 0xFFFFFFFF

    def __init__(self, server):
        '''
        Initialize a server disconnected exception
        '''
        self.server = server
        self.message = 'Server [{0}] is not connected'.format(server)
        super(MemCacheServerDisconnectionException, self).__init__(self.message)

class MemCacheConnectionErrorException(MemCacheExceptionBase):

    def __init__(self, server, e):
        '''
        Initialize a connection error exception
        '''
        self.server = server
        self.exception = e
        self.message = 'Unable to connect to [{0}]: {1}'.format(str(server), e)
        super(MemCacheConnectionErrorException, self).__init__(self.message)

class MemCacheTimeoutException(MemCacheExceptionBase):

    def __init__(self, server, message=None):
        '''
        Initialize a connection error exception
        '''
        self.server = server
        self.message = 'Timeout while waiting for [{0}]'.format(server) if message is None else message
        super(MemCacheTimeoutException, self).__init__(self.message)

