from decouple import config


class Settings:

    # ============================================================
    # Database
    # ============================================================

    DATABASE_URL: str = config(
        "DATABASE_URL"
    )


    # ============================================================
    # JWT
    # ============================================================

    SECRET_KEY: str = config(
        "SECRET_KEY"
    )

    ALGORITHM: str = config(
        "ALGORITHM",
        default="HS256",
    )

    ACCESS_TOKEN_EXPIRE_MINUTES: int = config(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        cast=int,
        default=30,
    )


    # ============================================================
    # Email
    # ============================================================

    MAIL_USERNAME: str = config(
        "MAIL_USERNAME"
    )

    MAIL_PASSWORD: str = config(
        "MAIL_PASSWORD"
    )

    MAIL_FROM: str = config(
        "MAIL_FROM"
    )

    MAIL_PORT: int = config(
        "MAIL_PORT",
        cast=int,
        default=587,
    )

    MAIL_SERVER: str = config(
        "MAIL_SERVER",
        default="smtp.gmail.com",
    )

    MAIL_STARTTLS: bool = config(
        "MAIL_STARTTLS",
        cast=bool,
        default=True,
    )

    MAIL_SSL_TLS: bool = config(
        "MAIL_SSL_TLS",
        cast=bool,
        default=False,
    )


    # ============================================================
    # GitHub App
    # ============================================================

    GITHUB_APP_ID: str = config(
        "GITHUB_APP_ID",
        default="",
    )

    GITHUB_CLIENT_ID: str = config(
        "GITHUB_CLIENT_ID",
        default="",
    )

    GITHUB_CLIENT_SECRET: str = config(
        "GITHUB_CLIENT_SECRET",
        default="",
    )

    GITHUB_PRIVATE_KEY_PATH: str = config(
        "GITHUB_PRIVATE_KEY_PATH",
        default="",
    )

    GITHUB_WEBHOOK_SECRET: str = config(
        "GITHUB_WEBHOOK_SECRET",
        default="",
    )


    # ============================================================
    # Gemini
    # ============================================================

    GEMINI_API_KEY: str = config(
        "GEMINI_API_KEY",
        default="",
    )

    GEMINI_MODEL: str = config(
        "GEMINI_MODEL",
        default="gemini-3-flash-preview",
    )


    # ============================================================
    # OpenRouter
    # ============================================================

    OPENROUTER_API_KEY: str = config(
        "OPENROUTER_API_KEY",
        default="",
    )

    OPENROUTER_MODEL: str = config(
        "OPENROUTER_MODEL",
        default="google/gemma-4-31b-it:free",
    )


# ============================================================
# Settings Instance
# ============================================================

settings = Settings()