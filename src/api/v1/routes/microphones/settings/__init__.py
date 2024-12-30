from src.bases.api.routes import Route
from .logic_handlers import MicrophoneTrackingLogicHandler, GetMicrophoneTrackingLogicHandler


class MicrophoneSettingsRoute(Route):
    auth = False
    path = "/microphones/tracking"
    method = "post"

    logic_handler_class = MicrophoneTrackingLogicHandler


class GetMicrophoneSettingsRoute(Route):
    auth = False
    path = "/microphones/tracking"
    method = "get"

    logic_handler_class = GetMicrophoneTrackingLogicHandler
