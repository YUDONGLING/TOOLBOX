class Scheduler(object):
    '''
    A Scheduler for Background Tasks.
    '''
    def __init__(self, Name: str = 'Scheduler'):
        import threading

        self.Name = Name
        self.Task = []

        self._On = False
        self._Thread = None
        self._ThreadLock = threading.Lock()

    def _Worker(self):
        import time
        import croniter
        import threading

        print(f' * Serving Scheduler app \'{self.Name}\'')
        time.sleep(5)

        while self._On:
            Now = time.time()
            with self._ThreadLock:
                for _Config in self.Task:
                    _Run = False
                    if _Config['Cron'] is not None:
                        if Now >= _Config['NextRunBy']:
                            _Run = True; _Config['NextRunBy'] = croniter.croniter(_Config['Cron'], Now).get_next(float)
                    else:
                        if Now - _Config['LastRunBy'] >= _Config['Interval']:
                            _Run = True; _Config['NextRunBy'] = Now + _Config['Interval']

                    if _Run:
                        _Config['LastRunBy'] = Now
                        threading.Thread(target = self._Execute, args = (_Config), daemon = True).start()
            time.sleep(1)

    def _Execute(self, _Config):
        import time

        if not __package__:
              from  Log import MakeErrorMessage
        else: from .Log import MakeErrorMessage

        print('{Name} - - [{Time}] "- {Function} {TrigType}/{TrigCondition}" - -'.format(
            Name          = self.Name,
            Time          = time.strftime('%d/%b/%Y %H:%M:%S', time.localtime()),
            Function      = _Config['Function'].__name__,
            TrigType      = 'Cron' if _Config['Cron'] is not None else 'Interval',
            TrigCondition = _Config['Cron'] if _Config['Cron'] is not None else str(_Config['Interval'] * 1.0)
        ))

        try:
            Result = _Config['Function'](*_Config.get('Args', ()), **dict(_Config.get('Kwargs', {})))
            try   : Ec, Em = bool(Result.get('Ec')), Result.get('Em', '')
            except: Ec, Em = False, ''
        except Exception as Error:
            Ec, Em = True, MakeErrorMessage(Error)

        if Ec: print('%s     %s' % (' ' * len(self.Name), Em))

    def task(self, Interval = None, Cron = None, Args = None, Kwargs = None):
        import time
        import croniter

        def Decorator(Function):
            with self._ThreadLock:
                if Interval is None and Cron is None        : raise Exception(f'Either Interval or Cron Must Be Specified')
                if Interval is not None and Cron is not None: raise Exception(f'Cannot Specify Both Interval and Cron')

                if Cron is not None:
                    self.Task.append({
                        'Function' : Function,
                        'Interval' : None,
                        'Cron'     : Cron,
                        'LastRunBy': 0,
                        'NextRunBy': croniter.croniter(Cron).get_next(float),
                        'Args'     : Args or (),
                        'Kwargs'   : Kwargs or {}
                    })
                else:
                    self.Task.append({
                        'Function' : Function,
                        'Interval' : Interval,
                        'Cron'     : None,
                        'LastRunBy': 0,
                        'NextRunBy': time.time() + Interval,
                        'Args'     : Args or (),
                        'Kwargs'   : Kwargs or {}
                    })
            return Function
        return Decorator

    def run(self):
        import threading

        if not self._On:
            self._On = True
            self._Thread = threading.Thread(target = self._Worker, daemon = True)
            self._Thread.start()
        return True

    def stop(self):
        if self._On:
            self._On = False
            if self._Thread and self._Thread.is_alive(): self._Thread.join(timeout = 60)
        return True
