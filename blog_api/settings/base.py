from pathlib import Path

from .conf import DEBUG, PROJECT_DIR, SECRET_KEY, SIMPLE_JWT, settings  # noqa: F401

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
    "apps.categories.apps.CategoriesConfig",
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
    )
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
