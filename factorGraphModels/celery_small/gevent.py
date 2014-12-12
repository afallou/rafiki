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
    def on_start(self):