from dataclasses import dataclass
from datetime import timedelta
from enum import StrEnum
from pathlib import Path
from typing import Any, Callable, cast

import redis
from decouple import RepositoryEnv  # type: ignore
from decouple import config as decouple_config

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILES_DIR = BASE_DIR / "env_files"

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


secret_key_path: str = BASE_DIR / config("SECRET_KEY_PATH")

SECRET_KEY: str = Path(secret_key_path).read_text()
DEBUG: bool = config(
    "DEBUG", default=False, cast=lambda x: x.lower() in ("true", "yes", "1")
)
ALLOWED_HOSTS: list[str] = config("ALLOWED_HOSTS", default="localhost").split(",")

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

        avatar_max_size_in_bytes = 5 * 1024 * 1024
        avatar_max_size_in_megabytes = avatar_max_size_in_bytes / (1024 * 1024)
        avatar_formats = ["JPEG", "PNG", "WEBP"]

    @dataclass
    class Database:
        engine: str = config("BLOG_DB_ENGINE")

        user: str = config("BLOG_DB_USER")
        name: str = config("BLOG_DB_NAME")
        host: str = config("BLOG_DB_HOST")
        port: int = config("BLOG_DB_PORT", cast=int)

        @property
        def password(self) -> str:
            password_file = BASE_DIR / Path(config("BLOG_DB_PASSWORD_FILE"))
            return password_file.read_text()

    @dataclass
    class Auth:
        @dataclass
        class JWT:
            access_token_lifetime = timedelta(
                seconds=config("BLOG_JWT_ACCESS_LIFETIME", cast=int)
            )
            refresh_token_lifetime = timedelta(
                seconds=config("BLOG_JWT_REFRESH_LIFETIME", cast=int)
            )

            @property
            def private_key(self) -> str:
                private_key_path: Path = BASE_DIR / config("BLOG_JWT_PRIVATE_KEY_PATH")
                return private_key_path.read_text()

            @property
            def public_key(self) -> str:
                public_key_path: Path = BASE_DIR / config("BLOG_JWT_PUBLIC_KEY_PATH")
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

    class Log:
        level = config("LOG_LEVEL", default="INFO")

        debug_allowed = level == "DEBUG"
        info_allowed = level == "INFO"

    class Redis:
        @property
        def password(self) -> str:
            redis_password_path: Path = BASE_DIR / config("BLOG_REDIS_PASSWORD_FILE")
            return redis_password_path.read_text()

        host = "127.0.0.1"
        port = config("BLOG_REDIS_PORT", cast=int)

        class Prefix:
            post_list = "post_list"
            comment_list = "comment_list"
            user_list = "user_list"

        prefix = Prefix

    users = Users
    db = Database()
    auth = Auth()
    post = Post
    log = Log
    redis = Redis()


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

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{settings.redis.host}:{settings.redis.port}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": settings.redis.password,
        },
    }
}

redis_client = redis.Redis(
    host=settings.redis.host,
    port=settings.redis.port,
    password=settings.redis.password,
    db=0,
)
pubsub = redis_client.pubsub()


class Channels(StrEnum):
    COMMENTS = "comments"
