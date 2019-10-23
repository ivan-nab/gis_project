from rest_framework.exceptions import APIException


class ExternalServiceError(APIException):
    status_code = 503
    default_detail = 'Openroutesservice server error'
    default_code = 'external_service_error'