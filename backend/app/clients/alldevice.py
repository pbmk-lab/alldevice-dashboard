from __future__ import annotations

from typing import Any

import httpx

from backend.app.core.config import Settings


class UpstreamAPIError(RuntimeError):
    pass


class AlldeviceClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _auth_payload(self) -> dict[str, dict[str, str]]:
        return {
            "auth": {
                "username": self.settings.username,
                "password": self.settings.password,
                "key": self.settings.api_key,
            }
        }

    async def _post(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(
                timeout=self.settings.request_timeout_seconds
            ) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as exc:
            raise UpstreamAPIError(f"Upstream timeout for {url}") from exc
        except httpx.HTTPError as exc:
            raise UpstreamAPIError(f"Upstream HTTP error for {url}: {exc}") from exc
        except ValueError as exc:
            raise UpstreamAPIError(f"Invalid JSON from {url}") from exc

    async def fetch_downtime(
        self,
        date_start: str,
        date_end: str,
    ) -> dict[str, Any]:
        payload = {
            **self._auth_payload(),
            "date_start": date_start,
            "date_end": date_end,
        }
        return await self._post(self.settings.base_url, payload)

    async def fetch_task_reports(
        self,
        date_start: str,
        date_end: str,
    ) -> dict[str, Any]:
        payload = {
            **self._auth_payload(),
            "date_start": date_start,
            "date_end": date_end,
            "date_type": self.settings.taskreports_date_type,
        }
        return await self._post(self.settings.taskreports_url, payload)

    async def fetch_tasks(
        self,
        date_start: str,
        date_end: str,
    ) -> dict[str, Any]:
        payload = {
            **self._auth_payload(),
            "date_start": date_start,
            "date_end": date_end,
            "incomplete": 1,
            "show_used_spares": True,
            "limit": 200,
        }
        return await self._post(self.settings.tasks_url, payload)
