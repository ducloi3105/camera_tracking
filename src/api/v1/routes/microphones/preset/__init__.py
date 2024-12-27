from src.bases.api.routes import Route
from .logic_handlers import MicrophonePresetLogicHandler


class MicrophonePresetRoute(Route):
    auth = False
    path = "/microphones/{uid}/preset"
    method = "post"

    logic_handler_class = MicrophonePresetLogicHandler
