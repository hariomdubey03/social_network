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

USER_GET = {
    "user_code": {
        "type": "string",
        "regex": "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
        "minlength": 36,
        "maxlength": 36,
        "required": False,
    },
    "email_address": {
        "type": "string",
        "required": False,
        "empty": False,
        "regex": "^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$",
    },
}

USER_POST = {
    "name": {
        "type": "string",
        "minlength": 1,
        "maxlength": 100,
        "regex": "^[a-zA-Z\s]+$",
        "required": True,
    },
    "email_address": {
        "type": "string",
        "required": True,
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
