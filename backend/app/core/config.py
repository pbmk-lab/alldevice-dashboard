from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os
import tomllib
from urllib.parse import urljoin


class ConfigError(RuntimeError):
    pass


REPO_ROOT = Path(__file__).resolve().parents[3]
SECRETS_PATHS = [
    REPO_ROOT / ".streamlit" / "secrets.toml",
    REPO_ROOT.parent / ".streamlit" / "secrets.toml",
]
UPSTREAM_ENV_ALIASES: dict[str, tuple[str, ...]] = {
    "API_BASE_URL": ("ALLDEVICE_API_BASE_URL", "API_BASE_URL"),
    "BASE_URL": ("ALLDEVICE_BASE_URL", "BASE_URL"),
    "TASKREPORTS_URL": ("ALLDEVICE_TASKREPORTS_URL", "TASKREPORTS_URL"),
    "TASKS_URL": ("ALLDEVICE_TASKS_URL", "TASKS_URL"),
    "DOWNTIME_PATH": ("ALLDEVICE_DOWNTIME_PATH", "DOWNTIME_PATH"),
    "TASKREPORTS_PATH": ("ALLDEVICE_TASKREPORTS_PATH", "TASKREPORTS_PATH"),
    "TASKS_PATH": ("ALLDEVICE_TASKS_PATH", "TASKS_PATH"),
    "USERNAME": ("ALLDEVICE_USERNAME", "USERNAME"),
    "PASSWORD": ("ALLDEVICE_PASSWORD", "PASSWORD"),
    "API_KEY": ("ALLDEVICE_API_KEY", "API_KEY"),
}
DEFAULT_DOWNTIME_PATH = "/api/downtimes/list"
DEFAULT_TASKREPORTS_PATH = "/api/taskreports/list"
DEFAULT_TASKS_PATH = "/api/tasks/list"


def _read_secret_file() -> dict[str, str]:
    for secrets_path in SECRETS_PATHS:
        if secrets_path.exists():
            with secrets_path.open("rb") as handle:
                raw = tomllib.load(handle)
            return {key: str(value) for key, value in raw.items()}
    return {}


def _read_upstream_value(secret_file: dict[str, str], name: str, default: str = "") -> str:
    # Prefer the checked-in secrets contract over ambient OS env vars such as Windows USERNAME.
    if secret_file.get(name):
        return secret_file[name]

    for env_name in UPSTREAM_ENV_ALIASES.get(name, (name,)):
        value = os.getenv(env_name)
        if value:
            return value

    return default


def _join_api_url(base_url: str, path: str) -> str:
    if not base_url:
        return ""
    return urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))


def _derive_api_base_url(*urls: str) -> str:
    for url in urls:
        if not url:
            continue
        marker = "/api/"
        if marker in url:
            return url.split(marker, 1)[0]
    return ""


@dataclass(frozen=True)
class Settings:
    base_url: str
    taskreports_url: str
    tasks_url: str
    username: str
    password: str
    api_key: str
    default_date_start: str = "2023-01-01"
    default_date_end: str = "2026-12-31"
    taskreports_date_type: str = "completed_date"
    request_timeout_seconds: int = 30
    analysis_max_hours: int = 240
    default_locale: str = "lv"

    def require_upstream(self) -> None:
        missing = [
            name
            for name, value in (
                ("BASE_URL", self.base_url),
                ("TASKREPORTS_URL", self.taskreports_url),
                ("TASKS_URL", self.tasks_url),
                ("USERNAME", self.username),
                ("PASSWORD", self.password),
                ("API_KEY", self.api_key),
            )
            if not value
        ]
        if missing:
            raise ConfigError(
                "Missing required configuration values: " + ", ".join(missing)
            )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    secret_file = _read_secret_file()

    def read_value(name: str, default: str = "") -> str:
        return os.getenv(name, secret_file.get(name, default))

    api_base_url = _read_upstream_value(secret_file, "API_BASE_URL")
    downtime_path = _read_upstream_value(
        secret_file, "DOWNTIME_PATH", DEFAULT_DOWNTIME_PATH
    )
    taskreports_path = _read_upstream_value(
        secret_file, "TASKREPORTS_PATH", DEFAULT_TASKREPORTS_PATH
    )
    tasks_path = _read_upstream_value(secret_file, "TASKS_PATH", DEFAULT_TASKS_PATH)
    downtime_url = _read_upstream_value(secret_file, "BASE_URL")
    taskreports_url = _read_upstream_value(secret_file, "TASKREPORTS_URL")
    tasks_url = _read_upstream_value(secret_file, "TASKS_URL")

    if not downtime_url and api_base_url:
        downtime_url = _join_api_url(api_base_url, downtime_path)
    if not taskreports_url and api_base_url:
        taskreports_url = _join_api_url(api_base_url, taskreports_path)
    if not api_base_url:
        api_base_url = _derive_api_base_url(downtime_url, taskreports_url)
    if not tasks_url and api_base_url:
        tasks_url = _join_api_url(api_base_url, tasks_path)

    return Settings(
        base_url=downtime_url,
        taskreports_url=taskreports_url,
        tasks_url=tasks_url,
        username=_read_upstream_value(secret_file, "USERNAME"),
        password=_read_upstream_value(secret_file, "PASSWORD"),
        api_key=_read_upstream_value(secret_file, "API_KEY"),
        default_date_start=read_value("DEFAULT_DATE_START", "2023-01-01"),
        default_date_end=read_value("DEFAULT_DATE_END", "2026-12-31"),
        taskreports_date_type=read_value("TASKREPORTS_DATE_TYPE", "completed_date"),
        default_locale=read_value("DEFAULT_LOCALE", "lv"),
    )
