class TaskPool(BasePool):
    Timer = Timer
    signal_safe = False
    is_green = True
    task_join_will_block = False
    def __init__(self, *args, **kwargs):
        from gevent import spawn_raw
        from gevent.pool import Pool
        self.Pool = Pool
        self.spawn_n = spawn_raw
        self.timeout = kwargs.get('timeout')
        super(TaskPool, self).____init__(*args, **kwargs)
    try:
    def on_start(self):
        self._pool = self.Pool(self.limit)
        self._quick_put = self._pool.spawn
# line below is too long :(((( causes error - float division by zero when trying to calc error because # samples = 0 ????
def apply_timeout(target, args=(), kwargs={}, callback=None,
                  accept_callback=None, pid=None, timeout=None,
                  timeout_callback=None, Timeout=Timeout,
                  apply_target=apply_target, **rest):
