# SocialNetwork

Base URLs: http://localhost:8000

# User

## POST - Create User

POST - /v1/user/create

> Body Parameters

```json
{
  "name": "Bob Brown",
  "email_address": "bob.brown@example.com",
  "password": "another_hashed_password_here"
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| no |none|
|» name|body|string| yes |none|
|» email_address|body|string| yes |none|
|» password|body|string| yes |none|

> Response Examples

> Create User

```json
{
  "message": "User added successfully",
  "data": {
    "user_code": "6a540857-6126-11ef-b0eb-0045e2d691f3"
  }
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|Create User|Inline|

### Responses Data Schema

HTTP Status Code **201**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» message|string|true|none||none|
|» data|object|true|none||none|
|»» user_code|string|true|none||none|

## PATCH - Join Group

PATCH - /v1/user/join/cbb16afa-6126-11ef-b0eb-0045e2d691f3

> Body Parameters

```json
{}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| no |none|

> Response Examples

> Join Group

```json
{
  "message": "Joined group successfully",
  "data": null
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Join Group|Inline|

### Responses Data Schema

HTTP Status Code **200**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» message|string|true|none||none|
|» data|null|true|none||none|

## GET - Get User

GET - /v1/user/fetch

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|user_code|query|string| yes |none|
|email_address|query|string| yes |none|

> Response Examples

> Get User

```json
{
  "message": "User found successfully",
  "data": {
    "code": "6a540857-6126-11ef-b0eb-0045e2d691f3",
    "name": "Bob Brown",
    "email_address": "bob.brown@example.com"
  }
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Get User|Inline|

### Responses Data Schema

HTTP Status Code **200**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» message|string|true|none||none|
|» data|object|true|none||none|
|»» code|string|true|none||none|
|»» name|string|true|none||none|
|»» email_address|string|true|none||none|

# Auth

## POST - Login

POST - /v1/auth/login

> Body Parameters

```json
{
  "email_address": "bob.brown@example.com",
  "password": "another_hashed_password_here"
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| no |none|
|» email_address|body|string| yes |none|
|» password|body|string| yes |none|

> Response Examples

> Login

```json
{
  "message": "Access granted",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2NvZGUiOiI2YTU0MDg1Ny02MTI2LTExZWYtYjBlYi0wMDQ1ZTJkNjkxZjMiLCJleHAiOjE3MjQ0MDIyMzEsImlhdCI6MTcyNDQwMDQzMX0.zaLuY7AqysCFFpzGcXeFh1016kkG303O2AbwWmzAP3c",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2NvZGUiOiI2YTU0MDg1Ny02MTI2LTExZWYtYjBlYi0wMDQ1ZTJkNjkxZjMiLCJleHAiOjE3MjQ0MDQwMzEsImlhdCI6MTcyNDQwMDQzMX0.cuFTEmUdMmKBR56D9pg9yhSx7bZs8gDbAxkHrZxfi7Q"
  }
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Login|Inline|

### Responses Data Schema

HTTP Status Code **200**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» message|string|true|none||none|
|» data|object|true|none||none|
|»» access_token|string|true|none||none|
|»» refresh_token|string|true|none||none|

## POST - Regenerate Token

POST - /v1/auth/regenerate-token

> Body Parameters

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2NvZGUiOiIzNjhhOGY0Ni00OTc5LTExZWYtOTA3NS0wMDQ1ZTJkNjkxZjMiLCJleHAiOjE3MjE4MDA2OTEsImlhdCI6MTcyMTc5NzA5MX0.tsaVUHy1fRwq8tLGiN6lgaPDGKq66dMm12ywNOPLRa4"
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| no |none|
|» refresh_token|body|string| yes |none|

> Response Examples

> Regenerate Token

```json
{
  "message": "Token regenerated successfully",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2NvZGUiOiIzNjhhOGY0Ni00OTc5LTExZWYtOTA3NS0wMDQ1ZTJkNjkxZjMiLCJleHAiOjE3MjE3OTg5MjcsImlhdCI6MTcyMTc5NzEyN30.9x827we1eQfT33-D8chYmW_Z6_sQVCogrLOURLsicsA",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2NvZGUiOiIzNjhhOGY0Ni00OTc5LTExZWYtOTA3NS0wMDQ1ZTJkNjkxZjMiLCJleHAiOjE3MjE4MDA3MjcsImlhdCI6MTcyMTc5NzEyN30.aqxsr-MCkZCGCFN4sf37Ny3TIazqVaZgyTs7zl_PtWM"
  }
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|Regenerate Token|Inline|

### Responses Data Schema

HTTP Status Code **201**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» message|string|true|none||none|
|» data|object|true|none||none|
|»» access_token|string|true|none||none|
|»» refresh_token|string|true|none||none|

# Operations/Groups

## GET - Fetch Group

GET - /v1/ops/groups

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|user_code|query|string| yes |none|
|group_code|query|string| yes |none|

> Response Examples

> Fetch Group

```json
{
  "message": "Group found successfully",
  "data": [
    {
      "group_code": "0f4f3b24-6110-11ef-b0eb-0045e2d691f3",
      "name": "Travel Enthusiasts",
      "description": "A community for those who love to travel and explore new places."
    },
    {
      "group_code": "cbb16afa-6126-11ef-b0eb-0045e2d691f3",
      "name": "Book Club",
      "description": "Join us to discuss and review the latest books and literary classics."
    }
  ]
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Fetch Group|Inline|

### Responses Data Schema

HTTP Status Code **200**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» message|string|true|none||none|
|» data|[object]|true|none||none|
|»» group_code|string|true|none||none|
|»» name|string|true|none||none|
|»» description|string|true|none||none|

## POST - Create Group

POST - /v1/ops/groups

> Body Parameters

```json
{
  "name": "Book Club",
  "description": "Join us to discuss and review the latest books and literary classics."
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| no |none|
|» name|body|string| yes |none|
|» description|body|string| yes |none|

> Response Examples

> Create Group

```json
{
  "message": "Group created successfully",
  "data": {
    "group_code": "cbb16afa-6126-11ef-b0eb-0045e2d691f3"
  }
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|Create Group|Inline|

### Responses Data Schema

HTTP Status Code **201**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» message|string|true|none||none|
|» data|object|true|none||none|
|»» group_code|string|true|none||none|

## DELETE - Delete Group

DELETE - /v1/ops/groups/cbb16afa-6126-11ef-b0eb-0045e2d691f3

> Response Examples

> Delete Group

```json
{
  "message": "Group deleted successfully",
  "data": null
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|204|[No Content](https://tools.ietf.org/html/rfc7231#section-6.3.5)|Delete Group|Inline|

### Responses Data Schema

HTTP Status Code **204**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» message|string|true|none||none|
|» data|null|true|none||none|

# Operations/Posts

## GET - Fetch Post

GET - /v1/ops/groups/cbb16afa-6126-11ef-b0eb-0045e2d691f3/posts

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|post_code|query|string| yes |none|

> Response Examples

> Fetch Post

```json
{
  "message": "Post found successfully",
  "data": [
    {
      "name": "Alice Johnson",
      "post_code": "803dde33-6127-11ef-b0eb-0045e2d691f3",
      "content": "Just read 'The Great Gatsby' for the first time. A timeless classic!",
      "total_comments": null,
      "total_likes": null
    }
  ]
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Fetch Post|Inline|

### Responses Data Schema

HTTP Status Code **200**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» message|string|true|none||none|
|» data|[object]|true|none||none|
|»» name|string|false|none||none|
|»» post_code|string|false|none||none|
|»» content|string|false|none||none|
|»» total_comments|null|false|none||none|
|»» total_likes|null|false|none||none|

## POST - Create Post

POST - /v1/ops/groups/cbb16afa-6126-11ef-b0eb-0045e2d691f3/posts

> Body Parameters

```json
{
  "content": "Just read 'The Great Gatsby' for the first time. A timeless classic!"
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| no |none|
|» content|body|string| yes |none|

> Response Examples

> Create Post

```json
{
  "message": "Post created successfully",
  "data": {
    "post_code": "803dde33-6127-11ef-b0eb-0045e2d691f3"
  }
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|Create Post|Inline|

### Responses Data Schema

HTTP Status Code **201**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» message|string|true|none||none|
|» data|object|true|none||none|
|»» post_code|string|true|none||none|

## DELETE - Delete Post

DELETE - /v1/ops/posts/803dde33-6127-11ef-b0eb-0045e2d691f3

> Response Examples

> Delete Post

```json
{
  "message": "Post deleted successfully",
  "data": null
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Delete Post|Inline|

### Responses Data Schema

HTTP Status Code **200**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» message|string|true|none||none|
|» data|null|true|none||none|

# Operations/Likes

## GET - Fetch Likes

GET - /v1/ops/posts/803dde33-6127-11ef-b0eb-0045e2d691f3/likes

> Response Examples

> Fetch Likes

```json
{
  "message": "Likes found successfully",
  "data": [
    {
      "name": "Alice Johnson",
      "post_code": "803dde33-6127-11ef-b0eb-0045e2d691f3"
    }
  ]
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Fetch Likes|Inline|

### Responses Data Schema

HTTP Status Code **200**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» message|string|true|none||none|
|» data|[object]|true|none||none|
|»» name|string|false|none||none|
|»» post_code|string|false|none||none|

## POST - Toggle Like

POST - /v1/ops/posts/803dde33-6127-11ef-b0eb-0045e2d691f3/likes

> Response Examples

> Toggle Like

```json
{
  "message": "Action performed successfully",
  "data": null
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|204|[No Content](https://tools.ietf.org/html/rfc7231#section-6.3.5)|Toggle Like|Inline|

### Responses Data Schema

HTTP Status Code **204**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» message|string|true|none||none|
|» data|null|true|none||none|

# Operations/Comments

## GET - Fetch Comment

GET - /v1/ops/posts/803dde33-6127-11ef-b0eb-0045e2d691f3/comments

> Response Examples

> Fetch Comment

```json
{
  "message": "Comment found successfully",
  "data": [
    {
      "comment_code": "c1268e27-6127-11ef-b0eb-0045e2d691f3",
      "name": "Alice Johnson",
      "content": "This post is really insightful! Thanks for sharing your thoughts."
    }
  ]
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Fetch Comment|Inline|

### Responses Data Schema

HTTP Status Code **200**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» message|string|true|none||none|
|» data|[object]|true|none||none|
|»» comment_code|string|false|none||none|
|»» name|string|false|none||none|
|»» content|string|false|none||none|

## POST - Create Comment

POST - /v1/ops/posts/803dde33-6127-11ef-b0eb-0045e2d691f3/comments

> Body Parameters

```json
{
  "content": "This post is really insightful! Thanks for sharing your thoughts."
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| no |none|
|» content|body|string| yes |none|

> Response Examples

> Create Comment

```json
{
  "message": "Comment created successfully",
  "data": {
    "comment_code": "c1268e27-6127-11ef-b0eb-0045e2d691f3"
  }
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|Create Comment|Inline|

### Responses Data Schema

HTTP Status Code **201**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» message|string|true|none||none|
|» data|object|true|none||none|
|»» comment_code|string|true|none||none|
