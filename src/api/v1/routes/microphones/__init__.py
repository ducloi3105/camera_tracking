from src.bases.api.routes import Route
from .logic_handlers import MicrophoneLogicHandler


class MicrophoneRoute(Route):
    auth = False
    path = "/microphones"
    method = "get"

    logic_handler_class = MicrophoneLogicHandler
