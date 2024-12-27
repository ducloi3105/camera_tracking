import inspect
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from src.databases import Redis, Mongo
from src.bases.api.auth_handler import BaseAuthenticationHandler
from src.bases.error.api import HTTPError

from config import ENVIRONMENT


class RouteLogicHandler(object):
    def __init__(self,
                 request,
                 session,
                 redis,
                 mongo=None,
                 accessor=None,
                 accesses=None,
                 access_token=None,
                 logger=None
                 ):
        self.request = request
        self.redis = redis
        self.session = session
        self.mongodb = mongo.get_database()
        self.accessor = accessor
        self.accesses = accesses
        self.access_token = access_token
        self.logger = logger

    def run(self, **kwargs):
        raise NotImplementedError


class MetaRoute(type):
    def __new__(cls, class_name, bases, attrs):

        if not bases:
            return super().__new__(cls, class_name, bases, attrs)

        logic_handler_class = attrs.get('logic_handler_class')
        if not logic_handler_class:
            raise AttributeError('Missing logic_handler_class')

        if not issubclass(logic_handler_class, RouteLogicHandler):
            raise TypeError(
                f'{logic_handler_class} is not a valid RouteLogicHandler type'
            )

        handle_func = attrs.get('handle')
        if not handle_func:
            handle_func = cls.get_handle_function(bases)

        if not handle_func:
            return super().__new__(cls, class_name, bases, attrs)

        logic_handler = logic_handler_class.run

        parameters = dict()

        for param_name, param in inspect.signature(
                logic_handler
        ).parameters.items():
            parameters[param_name] = param

        handle_func_signature = inspect.signature(handle_func)

        request_param = handle_func_signature.parameters.get(
            'request'
        )
        if not request_param:
            raise TypeError('Missing request param in handle function')
        parameters['request'] = request_param

        def run(self, **kwargs):
            return handle_func(self, **kwargs)

        setattr(
            run,
            '__signature__',
            handle_func_signature.replace(parameters=list(parameters.values()))
        )
        attrs['run'] = run

        return super().__new__(cls, class_name, bases, attrs)

    @staticmethod
    def get_handle_function(bases: tuple):
        result = None

        for base in reversed(bases):
            result = getattr(base, 'handle', None)
            if result is not None:
                break

        return result


class Route(metaclass=MetaRoute):
    path = None
    auth = True
    method = 'get'
    actions = list()

    logic_handler_class = RouteLogicHandler
    auth_handler_class = BaseAuthenticationHandler

    def __init__(self,
                 sql_session_maker=None,
                 redis_config=None,
                 mongo_config=None,
                 logger=None
                 ):
        self.sql_session_maker = sql_session_maker
        self.redis_config = redis_config
        self.mongo_config = mongo_config
        self.logger = logger

    def handle(self, *, request: Request, **kwargs):
        session = None
        redis = None
        mongo = None

        if self.sql_session_maker:
            session = self.sql_session_maker()
        if self.redis_config:
            redis = Redis(**self.redis_config)
        if self.mongo_config:
            mongo = Mongo(self.mongo_config)
        auth_handler = BaseAuthenticationHandler(
            session=session,
            request=request
        )
        access_token, accessor = auth_handler.run()
        accesses = dict()

        if self.auth and not access_token:
            raise HTTPException(status_code=401)

        if self.auth and self.actions:
            self._validate_access()

        lh = self.logic_handler_class(
            session=session,
            mongo=mongo,
            redis=redis,
            request=request,
            accesses=accesses,
            accessor=accessor,
            access_token=access_token,
            logger=self.logger
        )

        error = None
        response = None

        try:
            response = lh.run(**kwargs)
        except Exception as e:
            error = e

        if session:
            session.close()

        if redis:
            redis.close()

        if error is not None:
            if isinstance(error, HTTPError):
                return JSONResponse(
                    status_code=error.status_code,
                    content=error.output()
                )

            if ENVIRONMENT == 'production':
                raise HTTPException(status_code=500, detail=str(error))

            raise error

        return response

    def _validate_access(self):
        pass

    def run(self):
        raise NotImplementedError
