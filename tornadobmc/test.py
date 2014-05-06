# -*- coding: utf-8 -*-

from client import Client
import tornado.ioloop
import tornado.web, tornado.httpserver
import datetime
from tornado.gen import coroutine

loremipsum = 1000*'Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Nam liber tempor cum soluta nobis eleifend option congue nihil imperdiet doming id quod mazim placerat facer possim assum. Typi non habent claritatem insitam; est usus legentis in iis qui facit eorum claritatem. Investigationes demonstraverunt lectores legere me lius quod ii legunt saepius. Claritas est etiam processus dynamicus, qui sequitur mutationem consuetudium lectorum. Mirum est notare quam littera gothica, quam nunc putamus parum claram, anteposuerit litterarum formas humanitatis per seacula quarta decima et quinta decima. Eodem modo typi, qui nunc nobis videntur parum clari, fiant sollemnes in futurum.'
servers = ['localhost']
cl = Client(servers)

@coroutine
def main():
    try:
        idx = yield cl.set('1000loremipsum', loremipsum, 10)
        print '1000 lorem ipsum stored at', servers[idx]
        val, idx = yield cl.get('1000loremipsum')
        if val == loremipsum:
            print '1000 lorem ipsum successfully loaded from', servers[idx]
        else:
            raise Exception('lorem ipsum does not match')
            
        try:
            val, idx = yield cl.get('testkeywhichhopefullydoesntexist')
        except Exception as e:
            print 'successfully didn\'t find key "testkeywhichhopefullydoesntexist"'
    except Exception as e:
        print e
    finally:
        tornado.ioloop.IOLoop.instance().stop()

tornado.ioloop.IOLoop.instance().add_callback(main)
tornado.ioloop.IOLoop.instance().start()

