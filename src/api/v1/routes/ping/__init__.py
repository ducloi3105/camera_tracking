from src.bases.api.routes import Route
from .logic_handlers import MicrophonesPingLogicHandler


class MicrophonesPingRoute(Route):
    auth = False
    path = "/ping"
    method = "get"

    logic_handler_class = MicrophonesPingLogicHandler
