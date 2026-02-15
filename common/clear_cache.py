from django.core.cache import cache


def clear_cache(prefix: str) -> None:
    cache.delete_many(keys=cache.keys(f"*.{prefix}.*"))  # type: ignore
