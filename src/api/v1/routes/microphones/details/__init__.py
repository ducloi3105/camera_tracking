from src.bases.api.routes import Route
from .logic_handlers import MicrophoneDetailsLogicHandler


class MicrophoneDetailsRoute(Route):
    auth = False
    path = "/microphones/{uid}/details"
    method = "get"

    logic_handler_class = MicrophoneDetailsLogicHandler
