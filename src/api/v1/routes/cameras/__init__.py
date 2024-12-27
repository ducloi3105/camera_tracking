from src.bases.api.routes import Route
from .logic_handlers import CamerasLogicHandler


class CameraRoute(Route):
    auth = False
    path = "/cameras"
    method = "get"

    logic_handler_class = CamerasLogicHandler
