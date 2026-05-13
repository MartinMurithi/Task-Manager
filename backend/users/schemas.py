from ninja import Schema
from pydantic import EmailStr

class RegisterSchema(Schema):
    username: str
    email: EmailStr
    password: str


class UserOutSchema(Schema):
    id: int
    username: str
    email: str
