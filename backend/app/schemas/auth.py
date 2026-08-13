from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


BCRYPT_MAX_PASSWORD_BYTES = 72


class PasswordMixin(BaseModel):
    password: str = Field(
        min_length=8,
        max_length=64,
    )

    @field_validator("password")
    @classmethod
    def validate_bcrypt_password_length(
        cls,
        password: str,
    ) -> str:

        if len(password.encode("utf-8")) > BCRYPT_MAX_PASSWORD_BYTES:
            raise ValueError(
                "Password must be at most 72 bytes "
                "when encoded as UTF-8"
            )

        return password


class UserRegister(PasswordMixin):
    model_config = ConfigDict(
        populate_by_name=True
    )

    name: str = Field(
        validation_alias=AliasChoices(
            "name",
            "full_name",
        )
    )

    email: EmailStr


class UserLogin(PasswordMixin):
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(
        min_length=8,
        max_length=64,
    )

    @field_validator("new_password")
    @classmethod
    def validate_bcrypt_password_length(
        cls,
        password: str,
    ) -> str:

        if len(password.encode("utf-8")) > BCRYPT_MAX_PASSWORD_BYTES:
            raise ValueError(
                "Password must be at most 72 bytes "
                "when encoded as UTF-8"
            )

        return password