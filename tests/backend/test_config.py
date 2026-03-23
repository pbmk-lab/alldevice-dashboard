from __future__ import annotations

from backend.app.core import config


def test_secret_username_wins_over_windows_username_env(monkeypatch) -> None:
    monkeypatch.setenv("USERNAME", "jurijs.veskins")
    monkeypatch.setattr(
        config,
        "_read_secret_file",
        lambda: {
            "BASE_URL": "https://example.com/base",
            "TASKREPORTS_URL": "https://example.com/reports",
            "USERNAME": "api-user",
            "PASSWORD": "api-password",
            "API_KEY": "api-key",
        },
    )
    config.get_settings.cache_clear()
    try:
        settings = config.get_settings()
        assert settings.username == "api-user"
    finally:
        config.get_settings.cache_clear()


def test_alldevice_username_env_alias_is_used_when_secret_missing(monkeypatch) -> None:
    monkeypatch.delenv("USERNAME", raising=False)
    monkeypatch.setenv("ALLDEVICE_USERNAME", "api-user-env")
    monkeypatch.setattr(
        config,
        "_read_secret_file",
        lambda: {
            "BASE_URL": "https://example.com/base",
            "TASKREPORTS_URL": "https://example.com/reports",
            "PASSWORD": "api-password",
            "API_KEY": "api-key",
        },
    )
    config.get_settings.cache_clear()
    try:
        settings = config.get_settings()
        assert settings.username == "api-user-env"
    finally:
        config.get_settings.cache_clear()
