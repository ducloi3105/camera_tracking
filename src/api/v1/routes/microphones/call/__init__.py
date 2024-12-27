from src.bases.api.routes import Route
from .logic_handlers import MicrophoneCallLogicHandler


class MicrophoneCallRoute(Route):
    auth = False
    path = "/microphones/{uid}/call"
    method = "post"

    logic_handler_class = MicrophoneCallLogicHandler
