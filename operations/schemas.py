# Schema for Authentication Token
GROUP_GET = {
    "group_code": {
        "type": "string",
        "maxlength": 255,
        "required": False,
    },
    "user_code": {
        "type": "string",
        "maxlength": 255,
        "required": False,
    },
}
# Schema for Regenerate Token
COMMENT_POST = {
    "content": {
        "type": "string",
        "required": True,
    }
}
COMMENT_PATCH = {
    "content": {
        "type": "string",
        "required": True,
    }
}

GROUP_POST = {
    "name": {"type": "string", "required": True, "empty": False},
    "description": {"type": "string", "required": True, "empty": False},
}

POSTS_GET = {
    "post_code": {
        "type": "string",
        "maxlength": 255,
        "required": False,
        "empty": False,
    },
}
POSTS_POST = {
    "content": {"type": "string", "required": True, "empty": False},
}
