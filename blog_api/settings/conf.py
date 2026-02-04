from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any, Callable, cast

from decouple import RepositoryEnv  # type: ignore
from decouple import config as decouple_config

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILES_DIR = PROJECT_DIR / "env_files"

environment: str = cast(str, decouple_config("ENV", default="dev"))

env_template_path = ENV_FILES_DIR / ".env.template"

if environment == "dev":
    env_path = ENV_FILES_DIR / ".env.dev"
elif environment == "test":
    env_path = ENV_FILES_DIR / ".env.test"
elif environment == "light":
    env_path = ENV_FILES_DIR / ".env.light"
else:
    raise ValueError("ENV environment variable is not set. Use 'dev' or 'test'.")


template_repository = RepositoryEnv(env_template_path)
env_repository = RepositoryEnv(env_path)


def config(
    name: str, default: Any | None = None, cast: Callable[[str], Any] | None = None
) -> Any:
    """
    Get configuration value with template override support.

    Template provides base values, environment file overrides them.

    Args:
        name: Environment variable name
        default: Default value if not found
        cast: Type converter (e.g., bool, int)

    Raises:
        RuntimeError: if environment variable missing and no default
        ValueError: if cast fails
    """

    result = default

    if name in template_repository:
        result = template_repository[name]
    if name in env_repository:
        result = env_repository[name]

    if result is None:
        raise RuntimeError(f"Environment variable '{name}' not found.")

    if cast is not None:
        return cast(result)

    return result


secret_key_path: str = PROJECT_DIR / config("SECRET_KEY_PATH")

SECRET_KEY: str = Path(secret_key_path).read_text()
DEBUG: bool = config(
    "DEBUG", default=False, cast=lambda x: x.lower() in ("true", "yes", "1")
)


# ==============================
# ==== Application Settings ====
# ==============================


@dataclass
class Settings:

    class Users:
        email_length: int = 255
        avatars_dir: Path = Path("users/avatars")

        first_name_max_length = 50
        last_name_max_length = 50

    @dataclass
    class Database:
        engine: str = config("BLOG_DB_ENGINE")

        user: str = config("BLOG_DB_USER")
        name: str = config("BLOG_DB_NAME")
        host: str = config("BLOG_DB_HOST")
        port: int = config("BLOG_DB_PORT", cast=int)

        @property
        def password(self) -> str:
            password_file = PROJECT_DIR / Path(config("BLOG_DB_PASSWORD_FILE"))
            return password_file.read_text()

    @dataclass
    class Auth:
        @dataclass
        class JWT:
            access_token_lifetime = timedelta(minutes=15)
            refresh_token_lifetime = timedelta(days=15)

            @property
            def private_key(self) -> str:
                private_key_path: Path = PROJECT_DIR / config(
                    "BLOG_JWT_PRIVATE_KEY_PATH"
                )
                return private_key_path.read_text()

            @property
            def public_key(self) -> str:
                public_key_path: Path = PROJECT_DIR / config("BLOG_JWT_PUBLIC_KEY_PATH")
                return public_key_path.read_text()

        class Password:
            min_length = 8
            max_length = 128
            min_entropy = 50

        jwt = JWT()
        password = Password

    class Post:
        title_max_length = 200
        body_max_length = 5000

    users = Users
    db = Database()
    auth = Auth()
    post = Post


settings = Settings()


SIMPLE_JWT = {
    "ALGORITHM": "RS256",
    "SIGNING_KEY": settings.auth.jwt.private_key,
    "VERIFYING_KEY": settings.auth.jwt.public_key,
    "ACCESS_TOKEN_LIFETIME": settings.auth.jwt.access_token_lifetime,
    "REFRESH_TOKEN_LIFETIME": settings.auth.jwt.refresh_token_lifetime,
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}
