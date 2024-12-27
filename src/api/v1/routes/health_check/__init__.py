from src.bases.api.routes import Route
from .logic_handlers import HealthCheckLogicHandler


class HealthCheck(Route):
    auth = False
    path = "/health-check"
    method = "get"

    logic_handler_class = HealthCheckLogicHandler
