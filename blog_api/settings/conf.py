from dataclasses import dataclass
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

    @dataclass
    class Users:
        email_length: int = 255
        avatars_dir: Path = Path("users/avatars")

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

    users = Users()
    db = Database()


settings = Settings()
