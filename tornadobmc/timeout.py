# -*- coding: utf-8 -*-

from tornado.ioloop import IOLoop
from tornado.gen import YieldPoint, Wait

#
# This class was extracted from Jiryu Davis' Yieldpoint project, available at: https://github.com/ajdavis/yieldpoints
# It is distributed under the Apache 2.0 License, which you may obtain here: http://www.apache.org/licenses/LICENSE-2.0
#
# It was only modified to permit specifying the exception class to throw.
#

class WithTimeout(YieldPoint):
    """Wait for a YieldPoint or a timeout, whichever comes first.

    :Parameters:
      - `deadline`: A timestamp or timedelta
      - `yield_point`: A ``gen.YieldPoint`` or a key
      - `io_loop`: Optional custom ``IOLoop`` on which to run timeout
    """
    def __init__(self, deadline, yield_point, io_loop=None, exception=None):
        self.deadline = deadline
        self.exception = exception
        if isinstance(yield_point, YieldPoint):
            self.yield_point = yield_point
        else:
            # yield_point is actually a key, e.g. gen.Callback('key')
            self.yield_point = Wait(yield_point)
        self.expired = False
        self.timeout = None
        self.io_loop = io_loop or IOLoop.instance()

    def start(self, runner):
        self.runner = runner
        self.timeout = self.io_loop.add_timeout(self.deadline, self.expire)
        self.yield_point.start(runner)

    def is_ready(self):
        return self.expired or self.yield_point.is_ready()

    def get_result(self):
        if self.expired:
            if self.exception is None:
                raise Exception('Timeout')
            else:
                raise self.exception

        return self.yield_point.get_result()

    def expire(self):
        self.expired = True
        self.runner.run()

