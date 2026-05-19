from pydantic import BaseModel, validator


class UserCreate(BaseModel):

    username: str

    email: str

    password: str

    @validator("email")
    def email_must_be_intimetec(cls, value):
        if not value or not value.lower().endswith("@intimetec.com"):
            raise ValueError("Email must end with @intimetec.com")
        return value