# Schema for Authentication Token
AUTHENTICATION_TOKEN_POST = {
    "platform_code": {
        "type": "string",
        "maxlength": 255,
        "required": True,
    }
}
# Schema for Regenerate Token
REGENERATE_TOKEN_POST = {
    "refresh_token": {
        "type": "string",
        "maxlength": 255,
        "required": True,
    }
}

LOGIN_POST = {
    "email_address": {
        "type": "string",
        "required": False,
        "empty": False,
        "regex": "^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$",
    },
    "password": {
        "type": "string",
        "minlength": 6,
        "empty": False,
        "required": True,
    },
}
