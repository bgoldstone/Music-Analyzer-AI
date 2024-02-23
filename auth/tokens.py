import jwt

# FOR DEVELOPMENT USE ONLY
JWT_SECRET = 'asdjqwee4yrhi8o234ry7fhikuhfgyuwiegbfeyiwkebvryuqgsbdhj@#!!#!$RDSIUEHOIJE'
JWT_ALGORITHM = 'HS256'


def create_token(user_id: int) -> str:
    return jwt.encode({'user_id': user_id}, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


def validate_token(token: str) -> bool:
    try:
        decode_token(token)
        return True
    except:
        return False
