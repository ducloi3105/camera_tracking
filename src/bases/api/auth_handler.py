from src.bases.error.api import ServerError
from src.bases.error.service import ServiceError


class AuthenticationHandler(object):
    def __init__(self, request, session):
        self.request = request
        self.session = session

    def run(self):
        """Return User or None"""
        raise NotImplementedError


class BaseAuthenticationHandler(AuthenticationHandler):
    def run(self):
        # auth_data = self.request.headers.get('Authorization', None)
        # if not auth_data:
        #     return None, None
        #
        # try:
        #     bearer, access_token = auth_data.split(' ')
        # except ValueError:
        #     return None, None
        #
        # if bearer != 'Bearer' or not access_token:
        #     return None, None
        #
        # iam_service = IamService()
        # try:
        #     accessor = iam_service.decode_token(access_token)
        #
        # except ServiceError as e:
        #     if e.error == 'BadRequestParams':
        #         return None, None
        #     raise ServerError(e.error, e.message)
        return None, {}
        # return access_token, accessor
