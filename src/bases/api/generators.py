import os
import sys
import importlib
import inspect
import logging
import tracemalloc
import sentry_sdk
import json
from fastapi import FastAPI, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic_core import PydanticUndefinedType
from sqlalchemy.orm import sessionmaker
from fastapi_profiler import PyInstrumentProfilerMiddleware
from contextlib import asynccontextmanager

from src.bases.api.routes import Route
from src.bases.api.middlewares import CorsMiddleware
from src.bases.api.logging_handlers import LoggingJsonFormatter
from src.common.constants import TMP_DIR
from config import ENVIRONMENT


class ApiGenerator(object):
    def __init__(
            self,
            router_modules: list,
            sql_session_maker: sessionmaker = None,
            mongo_config: dict = None,
            redis_config: dict = None,
            middlewares: list = None,
            sentry_dns: str = None,
            logger: logging.RootLogger = None,
    ):
        self.router_modules = router_modules
        self.redis_config = redis_config
        self.mongo_config = mongo_config
        self.sql_session_maker = sql_session_maker
        self.middlewares = middlewares or []
        self.logger = logger
        self.sentry_dns = sentry_dns

    def _add_routers(self, app: FastAPI):
        for router_module in self.router_modules:
            router = getattr(router_module, 'router', None)
            if not router:
                continue

            root_path = router_module.__name__.split('.')
            root_dir = os.path.dirname(router_module.__file__)
            if sys.platform == 'linux':
                dir_separator = '/'
            else:
                dir_separator = '\\'

            route_classes = []

            for dir_path, dir_names, file_names in os.walk(root_dir):
                diff = os.path.relpath(dir_path, root_dir)
                if diff == '.':
                    diff_dirs = []
                else:
                    diff_dirs = diff.split(dir_separator)
                target_pack_prefix = root_path + diff_dirs
                for dir_name in dir_names:
                    try:
                        target_pack = target_pack_prefix + [dir_name]
                        module = importlib.import_module('.'.join(target_pack))
                        classes = inspect.getmembers(module,
                                                     inspect.isclass)
                        for cls_name, cls in classes:
                            if not issubclass(cls, Route):
                                continue

                            if cls is Route:
                                continue

                            route_classes.append(cls)
                    except:
                        pass

            for rc in route_classes:
                route = rc(
                    redis_config=self.redis_config,
                    mongo_config=self.mongo_config,
                    sql_session_maker=self.sql_session_maker,
                    logger=self.logger
                )
                router.add_api_route(
                    path=route.path,
                    endpoint=route.run,
                    methods=[route.method],
                )

            app.include_router(router)

        return app

    def _add_middlewares(self, app: FastAPI):
        for md in self.middlewares:
            app.add_middleware(md)

        return app

    def _config_cors(self, app: FastAPI):

        app.add_middleware(
            CorsMiddleware,
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )

        return app

    def _config_exception_handlers(self, app):
        @app.exception_handler(RequestValidationError)
        def handle_rq_validation_err(
                _req: Request, exc: RequestValidationError
        ) -> JSONResponse:
            """Handle request validation errors."""

            errors = exc.errors()
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    'error': 'BadRequestParams',
                    'message': json.dumps(errors, default=str),
                    'meta': jsonable_encoder(
                        errors,
                        custom_encoder={
                            PydanticUndefinedType: lambda _: None,
                        },
                    )
                },
            )

    def _config_logger(self, app):
        handler = logging.StreamHandler()
        handler.setFormatter(LoggingJsonFormatter())
        self.logger.handlers = [handler]
        self.logger.setLevel(logging.DEBUG)
        logging.getLogger('uvicorn.access').disabled = True

        setattr(app, 'logger', self.logger)

        return app

    def _add_profiler(self, app):
        app.add_middleware(
            PyInstrumentProfilerMiddleware,
            server_app=app,
            is_print_each_request=True,
            profiler_output_type='html',
            open_in_browser=True,
            html_file_name=os.path.join(TMP_DIR, 'api_profile.html')
        )
        return app

    def _setup_lifespan(self, with_tracemalloc: bool = False) -> callable:
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            if with_tracemalloc:
                tracemalloc.start()

            yield

            if with_tracemalloc:
                snapshot = tracemalloc.take_snapshot()
                top_stats = snapshot.statistics('traceback')

                # pick the biggest memory block
                for stat in top_stats[:20]:
                    print("%s memory blocks: %.1f KiB" % (
                        stat.count, stat.size / 1024))
                    for line in stat.traceback.format():
                        print(line)
        return lifespan

    def _config_sentry(self):
        sentry_sdk.init(
            dsn=self.sentry_dns,
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            traces_sample_rate=1.0,
            # Set profiles_sample_rate to 1.0 to profile 100%
            # of sampled transactions.
            # We recommend adjusting this value in production.
            environment=ENVIRONMENT
        )

    def run(self,
            title: str,
            with_profiler: bool = False,
            with_tracemalloc: bool = False
            ) -> FastAPI:

        if self.sentry_dns:
            self._config_sentry()

        lifespan = self._setup_lifespan(
            with_tracemalloc=with_tracemalloc
        )

        app = FastAPI(title=title, lifespan=lifespan)

        if self.logger:
            self._config_logger(app)

        if with_profiler:
            self._add_profiler(app)

        self._add_middlewares(app)

        self._config_cors(app)
        self._config_exception_handlers(app)

        self._add_routers(app)

        return app
