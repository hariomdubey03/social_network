from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            "message": (
                response.data["message"]
                if response.data.get("message")
                else response.data["detail"]
            ),
            "data": (
                response.data["data"]
                if response.data.get("data")
                else None
            ),
        }

    return response
