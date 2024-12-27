from src.bases.error.base import BaseError


class Runner(object):
    def __init__(self, mongodb, jobs, logger=None):
        self.mongodb = mongodb
        self.jobs = jobs
        self.logger = logger

    def run(self, job_name: str, **options):
        if job_name not in self.jobs:
            raise BaseError(
                'InvalidParams',
                f'Job not found: {job_name}'
            )

        job = self.jobs[job_name]
        job_instance = job(self.mongodb, logger=self.logger)
        job_instance.run(**options)
