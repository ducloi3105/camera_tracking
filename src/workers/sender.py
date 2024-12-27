from src.bases.workers.generator import CeleryWorkerGenerator

from config import CeleryConfig

generator = CeleryWorkerGenerator(
    name='Worker',
    config=CeleryConfig,
)

sender = generator.run()
