from src.bases.workers.task import Task, LogicHandler as BaseLogicHandler


class LogicHandler(BaseLogicHandler):
    def run(self):
        print('testing')

class Testing(Task):
    logic_handler_class = LogicHandler
