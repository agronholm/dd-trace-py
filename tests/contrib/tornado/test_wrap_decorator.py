from nose.tools import eq_, ok_

from .utils import TornadoTestCase


class TestTornadoWebWrapper(TornadoTestCase):
    """
    Ensure that Tracer.wrap() works with Tornado web handlers.
    """
    def test_nested_wrap_handler(self):
        # it should trace a handler that calls a coroutine
        response = self.fetch('/nested_wrap/')
        eq_(200, response.code)
        traces = self.tracer.writer.pop_traces()
        eq_(1, len(traces))
        eq_(2, len(traces[0]))
        # check request span
        request_span = traces[0][0]
        eq_('tornado-web', request_span.service)
        eq_('tornado.request', request_span.name)
        eq_('http', request_span.span_type)
        eq_('tests.contrib.tornado.web.app.NestedWrapHandler', request_span.resource)
        eq_('GET', request_span.get_tag('http.method'))
        eq_('200', request_span.get_tag('http.status_code'))
        eq_('/nested_wrap/', request_span.get_tag('http.url'))
        eq_(0, request_span.error)
        # check nested span
        nested_span = traces[0][1]
        eq_('tornado-web', nested_span.service)
        eq_('tornado.coro', nested_span.name)
        eq_(0, nested_span.error)
        # check durations because of the yield sleep
        ok_(request_span.duration >= 0.05)
        ok_(nested_span.duration >= 0.05)

    def test_nested_exception_wrap_handler(self):
        # it should trace a handler that calls a coroutine that raises an exception
        response = self.fetch('/nested_exception_wrap/')
        eq_(500, response.code)
        traces = self.tracer.writer.pop_traces()
        eq_(1, len(traces))
        eq_(2, len(traces[0]))
        # check request span
        request_span = traces[0][0]
        eq_('tornado-web', request_span.service)
        eq_('tornado.request', request_span.name)
        eq_('http', request_span.span_type)
        eq_('tests.contrib.tornado.web.app.NestedExceptionWrapHandler', request_span.resource)
        eq_('GET', request_span.get_tag('http.method'))
        eq_('500', request_span.get_tag('http.status_code'))
        eq_('/nested_exception_wrap/', request_span.get_tag('http.url'))
        eq_(1, request_span.error)
        eq_('Ouch!', request_span.get_tag('error.msg'))
        ok_('Exception: Ouch!' in request_span.get_tag('error.stack'))
        # check nested span
        nested_span = traces[0][1]
        eq_('tornado-web', nested_span.service)
        eq_('tornado.coro', nested_span.name)
        eq_(1, nested_span.error)
        eq_('Ouch!', nested_span.get_tag('error.msg'))
        ok_('Exception: Ouch!' in nested_span.get_tag('error.stack'))
        # check durations because of the yield sleep
        ok_(request_span.duration >= 0.05)
        ok_(nested_span.duration >= 0.05)

    def test_sync_nested_wrap_handler(self):
        # it should trace a handler that calls a coroutine
        response = self.fetch('/sync_nested_wrap/')
        eq_(200, response.code)
        traces = self.tracer.writer.pop_traces()
        eq_(1, len(traces))
        eq_(2, len(traces[0]))
        # check request span
        request_span = traces[0][0]
        eq_('tornado-web', request_span.service)
        eq_('tornado.request', request_span.name)
        eq_('http', request_span.span_type)
        eq_('tests.contrib.tornado.web.app.SyncNestedWrapHandler', request_span.resource)
        eq_('GET', request_span.get_tag('http.method'))
        eq_('200', request_span.get_tag('http.status_code'))
        eq_('/sync_nested_wrap/', request_span.get_tag('http.url'))
        eq_(0, request_span.error)
        # check nested span
        nested_span = traces[0][1]
        eq_('tornado-web', nested_span.service)
        eq_('tornado.func', nested_span.name)
        eq_(0, nested_span.error)
        # check durations because of the yield sleep
        ok_(request_span.duration >= 0.05)
        ok_(nested_span.duration >= 0.05)

    def test_sync_nested_exception_wrap_handler(self):
        # it should trace a handler that calls a coroutine that raises an exception
        response = self.fetch('/sync_nested_exception_wrap/')
        eq_(500, response.code)
        traces = self.tracer.writer.pop_traces()
        eq_(1, len(traces))
        eq_(2, len(traces[0]))
        # check request span
        request_span = traces[0][0]
        eq_('tornado-web', request_span.service)
        eq_('tornado.request', request_span.name)
        eq_('http', request_span.span_type)
        eq_('tests.contrib.tornado.web.app.SyncNestedExceptionWrapHandler', request_span.resource)
        eq_('GET', request_span.get_tag('http.method'))
        eq_('500', request_span.get_tag('http.status_code'))
        eq_('/sync_nested_exception_wrap/', request_span.get_tag('http.url'))
        eq_(1, request_span.error)
        eq_('Ouch!', request_span.get_tag('error.msg'))
        ok_('Exception: Ouch!' in request_span.get_tag('error.stack'))
        # check nested span
        nested_span = traces[0][1]
        eq_('tornado-web', nested_span.service)
        eq_('tornado.func', nested_span.name)
        eq_(1, nested_span.error)
        eq_('Ouch!', nested_span.get_tag('error.msg'))
        ok_('Exception: Ouch!' in nested_span.get_tag('error.stack'))
        # check durations because of the yield sleep
        ok_(request_span.duration >= 0.05)
        ok_(nested_span.duration >= 0.05)

    def test_nested_wrap_executor_handler(self):
        # it should trace a handler that calls a blocking function in a different executor
        response = self.fetch('/executor_wrap_handler/')
        eq_(200, response.code)
        traces = self.tracer.writer.pop_traces()
        eq_(1, len(traces))
        eq_(2, len(traces[0]))
        # check request span
        request_span = traces[0][0]
        eq_('tornado-web', request_span.service)
        eq_('tornado.request', request_span.name)
        eq_('http', request_span.span_type)
        eq_('tests.contrib.tornado.web.app.ExecutorWrapHandler', request_span.resource)
        eq_('GET', request_span.get_tag('http.method'))
        eq_('200', request_span.get_tag('http.status_code'))
        eq_('/executor_wrap_handler/', request_span.get_tag('http.url'))
        eq_(0, request_span.error)
        # check nested span in the executor
        nested_span = traces[0][1]
        eq_('tornado-web', nested_span.service)
        eq_('tornado.executor.wrap', nested_span.name)
        eq_(0, nested_span.error)
        # check durations because of the yield sleep
        ok_(request_span.duration >= 0.05)
        ok_(nested_span.duration >= 0.05)

    def test_nested_exception_wrap_executor_handler(self):
        # it should trace a handler that calls a blocking function in a different
        # executor that raises an exception
        response = self.fetch('/executor_wrap_exception/')
        eq_(500, response.code)
        traces = self.tracer.writer.pop_traces()
        eq_(1, len(traces))
        eq_(2, len(traces[0]))
        # check request span
        request_span = traces[0][0]
        eq_('tornado-web', request_span.service)
        eq_('tornado.request', request_span.name)
        eq_('http', request_span.span_type)
        eq_('tests.contrib.tornado.web.app.ExecutorExceptionWrapHandler', request_span.resource)
        eq_('GET', request_span.get_tag('http.method'))
        eq_('500', request_span.get_tag('http.status_code'))
        eq_('/executor_wrap_exception/', request_span.get_tag('http.url'))
        eq_(1, request_span.error)
        eq_('Ouch!', request_span.get_tag('error.msg'))
        ok_('Exception: Ouch!' in request_span.get_tag('error.stack'))
        # check nested span
        nested_span = traces[0][1]
        eq_('tornado-web', nested_span.service)
        eq_('tornado.executor.wrap', nested_span.name)
        eq_(1, nested_span.error)
        eq_('Ouch!', nested_span.get_tag('error.msg'))
        ok_('Exception: Ouch!' in nested_span.get_tag('error.stack'))
        # check durations because of the yield sleep
        ok_(request_span.duration >= 0.05)
        ok_(nested_span.duration >= 0.05)
