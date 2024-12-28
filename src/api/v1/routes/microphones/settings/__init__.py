from src.bases.api.routes import Route
from .logic_handlers import MicrophoneTrackingLogicHandler


class MicrophoneDetailsRoute(Route):
    auth = False
    path = "/microphones/tracking"
    method = "get"

    logic_handler_class = MicrophoneTrackingLogicHandler
