import inspect
import logging
from kombu import Queue

from celery import Celery as _Celery
from celery.utils.log import get_logger

from .task import Task


class Celery(_Celery):
    def __init__(self,
                 redis=None,
                 mongodb=None,
                 logger=None,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.redis = redis
        self.mongodb = mongodb
        self.logger = logger

    def gen_task_name(self, name, module):
        return f'{self.main}.{name}'

    def send_task(self, name, queue=None, *args, **kwargs):
        name = f'{self.main}.{name}'
        if queue:
            queue = f'{self.main}.{queue}'

        return super().send_task(
            name=name,
            queue=queue,
            *args, **kwargs
        )


class CeleryWorkerGenerator(object):
    def __init__(self,
                 name: str,
                 config: object,
                 task_module=None,
                 redis=None,
                 mongodb=None,
                 task_queues=None,
                 schedulers=None):
        self.name = name
        self.config = config
        self.redis = redis
        self.mongodb = mongodb
        self.task_module = task_module
        self.task_queues = task_queues
        self.schedulers = schedulers

    def _register_task(self, worker):
        classes = inspect.getmembers(self.task_module,
                                     inspect.isclass)
        for cls_name, cls in classes:
            if not issubclass(cls, Task):
                continue

            worker.register_task(cls())

    @staticmethod
    def _setup_logger(worker):
        logger = get_logger(__name__)

        # clear default handlers
        for lh in logger.handlers:
            logger.removeHandler(lh)

        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(
            '%(asctime)s --  %(levelname)s  -- %(message)s'
        ))
        logger.setLevel(logging.INFO)
        logger.addHandler(ch)

        worker.logger = logger

    def _declare_queues(self, worker):
        queues = (
            Queue(f'{self.name}.{tq}')
            for tq in self.task_queues
        )
        worker.conf.task_queues = queues

    def _declare_beat_schedule(self, worker):
        beat_schedule = dict()

        for scheduler in self.schedulers:
            name = scheduler['name']
            task = scheduler['task']
            schedule = scheduler['schedule']
            queue = scheduler['queue']

            beat_schedule[f'{self.name}.{name}'] = {
                'task': f'{self.name}.{task.__name__}',
                'schedule': schedule,
                'options': {'queue': f'{self.name}.{queue}'}
            }

        worker.conf.beat_schedule = beat_schedule

    def run(self) -> Celery:
        worker = Celery(main=self.name,
                        redis=self.redis,
                        mongodb=self.mongodb)

        worker.config_from_object(self.config)

        if self.task_module:
            self._register_task(worker)

        if self.task_queues:
            self._declare_queues(worker)

        if self.schedulers:
            self._declare_beat_schedule(worker)

        self._setup_logger(worker)

        return worker
