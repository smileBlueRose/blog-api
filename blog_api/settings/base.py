from pathlib import Path

from .conf import (
    CACHES,
    DEBUG,
    PROJECT_DIR,
    SECRET_KEY,
    SIMPLE_JWT,
    settings,
)

_ = (DEBUG, PROJECT_DIR, SECRET_KEY, SIMPLE_JWT, settings, CACHES)

BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS: list[str] = []


DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
]
PROJECT_APPS = [
    "apps.users.apps.UsersConfig",
    "apps.posts.apps.PostsConfig",
    "apps.categories.apps.CategoriesConfig",
    "apps.comments.apps.CommentsConfig",
]
INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "middleware.requests.RequestIDMiddleware",
]

ROOT_URLCONF = "settings.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "settings.wsgi.application"


if settings.db.engine == "postgresql":
    database_config = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": settings.db.name,
            "USER": settings.db.user,
            "PASSWORD": settings.db.password,
            "HOST": settings.db.host,
            "PORT": settings.db.port,
        }
    }
elif settings.db.engine == "sqlite3":
    database_config = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "db.sqlite3",
        }
    }
else:
    raise RuntimeError(f"Unsupported database engine: {settings.db.engine}")

DATABASES = database_config

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "EXCEPTION_HANDLER": "middleware.exception_handlers.custom_exception_handler",
}


PASSWORD_HASHERS: list[str] = ["django.contrib.auth.hashers.Argon2PasswordHasher"]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"

MEDIA_ROOT = PROJECT_DIR / "media"
MEDIA_URL = "/media/"

AUTH_USER_MODEL = "users.User"

LOG_DIR = BASE_DIR / "logs"
DEBUG_LOG_PATH = LOG_DIR / "debug.log"
INFO_LOG_PATH = LOG_DIR / "info.log"
WARNING_LOG_PATH = LOG_DIR / "warning.log"
ERROR_LOG_PATH = LOG_DIR / "error.log"
CRITICAL_LOG_PATH = LOG_DIR / "critical.log"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} |{name:36s}|:{lineno:<4d} "
            "[{levelname:8s}] <{request_id:36s}> - {message}",
            "style": "{",
        },
        "simple": {
            "format": "[{levelname:8s}] - {message}",
            "style": "{",
        },
    },
    "filters": {
        "request_id": {
            "()": "settings.logger.RequestIDFilter",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "simple",
            "filters": ["request_id"],
        },
        "debug_file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": DEBUG_LOG_PATH,
            "formatter": "verbose",
            "maxBytes": 50 * 1024**2,
            "backupCount": 5,
            "filters": ["request_id"],
        },
        "info_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": INFO_LOG_PATH,
            "formatter": "verbose",
            "maxBytes": 10 * 1024**2,
            "backupCount": 10,
            "filters": ["request_id"],
        },
        "warning_file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": WARNING_LOG_PATH,
            "formatter": "verbose",
            "maxBytes": 5 * 1024**2,
            "backupCount": 3,
            "filters": ["request_id"],
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": ERROR_LOG_PATH,
            "formatter": "verbose",
            "maxBytes": 5 * 1024**2,
            "backupCount": 3,
            "filters": ["request_id"],
        },
        "critical_file": {
            "level": "CRITICAL",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": CRITICAL_LOG_PATH,
            "formatter": "verbose",
            "maxBytes": 5 * 1024**2,
            "backupCount": 3,
            "filters": ["request_id"],
        },
    },
    "loggers": {
        "django.utils.autoreload": {
            "level": "WARNING",
            "propagate": False,
        },
        "django": {
            "handlers": [
                "console",
                "debug_file",
                "info_file",
                "warning_file",
                "error_file",
                "critical_file",
            ],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": [
            "console",
            "debug_file",
            "info_file",
            "warning_file",
            "error_file",
            "critical_file",
        ],
        "level": settings.log.level,
    },
}
