# -*- coding: utf-8 -*-

from client import Client
import tornado.ioloop
import tornado.web, tornado.httpserver
import datetime, time
from tornado.gen import coroutine
from errors import *

loremipsum = 1000*'Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Nam liber tempor cum soluta nobis eleifend option congue nihil imperdiet doming id quod mazim placerat facer possim assum. Typi non habent claritatem insitam; est usus legentis in iis qui facit eorum claritatem. Investigationes demonstraverunt lectores legere me lius quod ii legunt saepius. Claritas est etiam processus dynamicus, qui sequitur mutationem consuetudium lectorum. Mirum est notare quam littera gothica, quam nunc putamus parum claram, anteposuerit litterarum formas humanitatis per seacula quarta decima et quinta decima. Eodem modo typi, qui nunc nobis videntur parum clari, fiant sollemnes in futurum.'
servers = ['localhost']
cl = Client(servers)

@coroutine
def main():
    try:
        key = '1000loremipsum{0}'.format(time.time())
        success, idx = yield cl.set(key, loremipsum, 10)
        print '1000 lorem ipsum stored at', servers[idx], 'success=', success
        
        val, idx = yield cl.get(key)
        if val == loremipsum:
            print '1000 lorem ipsum successfully loaded from', servers[idx]
        else:
            raise Exception('lorem ipsum does not match')
            
        try:
            val, idx = yield cl.get('testkeywhichhopefullydoesntexist')
        except MemCacheKeyNotFoundException as e:
            print 'successfully didn\'t find key "testkeywhichhopefullydoesntexist"'
        except Exception as e:
            print 'oops. exception:', e
            
        # test CAS. set initial value
        key = '99bottles{0}'.format(time.time())
        _99bottles = '99 bottles of beer on the wall, 99 bottles of beer, ...'
        success, idx = yield cl.set(key, _99bottles, 10)
        print '99 bottles stored at', servers[idx], 'success=', success
        
        # Get value
        val, idx, cas = yield cl.get(key, True)
        equal = val == _99bottles
        print 'got 99 bottles. read from', servers[idx], 'equal=', equal, 'cas=', cas

        # Try to update it with same CAS
        success, idx = yield cl.set(key, _99bottles+' if one falls down ...', 10, cas)
        print 'same CAS. success=', success, 'server=', servers[idx]
        
        # Try to update it with a different CAS (should fail!)
        success, idx = yield cl.set(key, _99bottles+' if one falls down ...', 10, cas-1)
        print 'different CAS. success=', success, 'server=', servers[idx]

    except Exception as e:
        print e
    finally:
        tornado.ioloop.IOLoop.instance().stop()

tornado.ioloop.IOLoop.instance().add_callback(main)
tornado.ioloop.IOLoop.instance().start()

