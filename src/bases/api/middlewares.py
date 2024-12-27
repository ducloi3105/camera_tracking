import time
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware


class CorsMiddleware(CORSMiddleware):
    def is_allowed_origin(self, origin: str) -> bool:
        if self.allow_all_origins:
            return True

        if (self.allow_origin_regex is not None
                and self.allow_origin_regex.fullmatch(origin)):
            return True

        if not self.allow_origins:
            return True

        return origin in self.allow_origins


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        logging_message = '{method} - {host}:{port}'.format(
            host=request.client.host,
            port=request.client.port,
            method=request.method.upper()
        )
        logging_data = dict(
            timestamp=datetime.utcnow().isoformat(),
            method=request.method.upper(),
            url=str(request.url),
        )

        response = await call_next(request)

        logging_data['status_code'] = response.status_code
        logging_data['res_time'] = round(time.time() - start_time, 4)

        if request.app.logger:
            request.app.logger.info(
                logging_message,
                extra=dict(
                    data=logging_data
                )
            )

        return response

