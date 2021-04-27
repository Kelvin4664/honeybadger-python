import sys

try:
    from celery import VERSION as CELERY_VERSION
    import celery.app.trace as trace
    from celery.app.task import Task
except ImportError:
    raise Exception("Celery installation not found")


from honeybadger import honeybadger
from honeybadger.plugins import Plugin
from honeybadger.utils import filter_dict, reraise

from threading import local


class CeleryPlugin(Plugin):

    def __init__(self):
        super(CeleryPlugin, self).__init__('CeleryPlugin')
        #Save reference to original build tracer
        self.original_build_tracer = trace.build_tracer
        trace.build_tracer = self._wrapped_build_tracer

    def _wrapped_build_tracer(self, name, task, *args, **kwargs):
        if not getattr(task, "_honeybadger_wrapped", False):
            task.__call__ = self._task_caller(task, task.__call__)
            task.run = self._task_caller(task, task.run)

            task._honeybadger_patched = True
        return self.original_build_tracer(name, task, *args, **kwargs)

    def _task_caller(self, task, f):
        
        def _inner(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                honeybadger.notify(e)
                exc_info = sys.exc_info()
                
                #Rerase exception to proceed with normal aws error handling
                reraise(*exc_info)

        return _inner  # type: ignore

    def supports(self, config, context):
        #Only celery version 3 and above is supported
        return CELERY_VERSION > (3, )

    def generate_payload(self, default_payload, config, context):
        """
        This plugin ensures celery exceptions are correctly monitored by honeybadger
        Can't think of any additional parameters to capture at this time.
        So we'll just return the payload as generated from the exception
        """
        return default_payload

    
