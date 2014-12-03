from __future__ import absolute_import
from time import time
try:
    from gevent import Timeout
except ImportError:
    Timeout = None
from kombu.async import timer as _timer
from .base import apply_target, BasePool
def apply_timeout(target, args=(), kwargs={}, callback=None,
                  accept_callback=None, pid=None, timeout=None,
                  timeout_callback=None, Timeout=Timeout,
                  apply_target=apply_target, **rest):
from __future__ import absolute_import
from time import time
try:
    from gevent import Timeout
except ImportError:
    Timeout = None
from kombu.async import timer as _timer
from .base import apply_target, BasePool
def apply_timeout(target, args=(), kwargs={}, callback=None,
                  accept_callback=None, pid=None, timeout=None,
                  timeout_callback=None, Timeout=Timeout,
                  apply_target=apply_target, **rest):