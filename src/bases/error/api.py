from src.bases.error.base import BaseError


class HTTPError(BaseError):
    status_code = 500

    def output(self):
        data = super(HTTPError, self).output()
        data['status_code'] = self.status_code
        return data


class MethodNotAllowed(HTTPError):
    status_code = 405
    message = 'Method not allowed.'


class AuthenticationError(HTTPError):
    status_code = 401
    message = 'Authentication error.'


class BadRequestParams(HTTPError):
    status_code = 400
    message = 'Bad request params.'


class PermissionError(HTTPError):
    status_code = 403
    message = 'Permission error.'


class ServiceNotAvailable(HTTPError):
    status_code = 503
    message = 'Service not available.'


class ServerError(HTTPError):
    status_code = 500
    message = 'Server error.'
