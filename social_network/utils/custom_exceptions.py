from rest_framework import status
from rest_framework.exceptions import APIException


class InternalServerError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Internal Server Error"
    default_code = "internal_server_error"


class DuplicateKey(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Duplicate Key in Field List"
    default_code = "duplicate_key"


class ExpiredSignatureError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Access token expired"
    default_code = "expired_signature_error"


class InvalidSignatureError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Access token is invalid"
    default_code = "invalid_signature_error"


class InvalidTokenError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Access token is invalid"
    default_code = "invalid_token_error"


class ResetKeyInvalid(APIException):
    status_code = status.HTTP_200_OK
    default_detail = "Password reset key not found"
    default_code = "reset_key_invalid"


class InvalidSlug(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid slug"
    default_code = "invalid_slug"


class InvalidAuthType(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid Auth Type"
    default_code = "invalid_auth_type"


class APIKeyMissing(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "API Key missing"
    default_code = "api_key_missing"


class AuthenticationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Authentication failed"
    default_code = "Authentication failed"


class DecodeError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Header string manipulated"
    default_code = "decode_error"


class APIKeyMissing(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "API Key missing"
    default_code = "api_key_missing"


class NotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Data does not exist"
    default_code = "does_not_exist"


class ValidationFailed(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Validations Failed."
    default_code = "validation_failed"


class VersionNotSupported(APIException):
    status_code = status.HTTP_505_HTTP_VERSION_NOT_SUPPORTED
    default_detail = "This version is not supported"
    default_code = "version_not_supported"


class ErrorMSG(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Unable to process the request"
    default_code = "unable_to_process"
