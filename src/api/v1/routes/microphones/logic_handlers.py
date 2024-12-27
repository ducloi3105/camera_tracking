from src.bases.api.routes import RouteLogicHandler


class HealthCheckLogicHandler(RouteLogicHandler):
    def run(self):
        return dict(success=True)
