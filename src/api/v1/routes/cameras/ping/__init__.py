from src.bases.api.routes import Route
from .logic_handlers import CameraPingLogicHandler


class CameraPingRoute(Route):
    auth = False
    path = "/camera/ping"
    method = "get"

    logic_handler_class = CameraPingLogicHandler
