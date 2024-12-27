from src.bases.workers.generator import CeleryWorkerGenerator
from src.databases import Redis, Mongo

from config import REDIS, CeleryConfig, MONGO_URI

from . import tasks

redis = Redis(**REDIS)

mongo = Mongo(MONGO_URI)

generator = CeleryWorkerGenerator(
    name='Worker',
    redis=redis,
    config=CeleryConfig,
    task_module=tasks,
    mongodb=mongo.get_database(),
    task_queues=(
        'CommonTasks',
    )
)

worker = generator.run()
