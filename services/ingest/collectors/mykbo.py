"""myKBO Stats collector.

Fetches raw HTML from mykbostats.com using httpx with browser-like headers.
"""

from __future__ import annotations

from datetime import date, datetime

import httpx

from ..models import CollectorError, RawSnapshot
from .base import BaseCollector

# Browser-like headers to avoid 403
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
        "Mobile/15E148 Safari/604.1"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# Base URL — update if the site structure changes
BASE_URL = "https://mykbostats.com"

# Timeout for all requests
REQUEST_TIMEOUT = 15.0


class MykboCollector(BaseCollector):
    """Collector for mykbostats.com."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers=DEFAULT_HEADERS,
                timeout=REQUEST_TIMEOUT,
                follow_redirects=True,
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def _fetch(self, url: str) -> RawSnapshot:
        """Fetch a URL and return a RawSnapshot."""
        client = await self._get_client()
        try:
            resp = await client.get(url)
            snapshot = RawSnapshot(
                url=url,
                html=resp.text,
                fetched_at=datetime.now(),
                status_code=resp.status_code,
            )
            if resp.status_code != 200:
                raise CollectorError(
                    url=url,
                    status_code=resp.status_code,
                    message=f"HTTP {resp.status_code}",
                )
            return snapshot
        except httpx.TimeoutException:
            raise CollectorError(url=url, status_code=None, message="Timeout")
        except httpx.HTTPError as e:
            raise CollectorError(url=url, status_code=None, message=str(e))

    async def fetch_game_list(self, target_date: date) -> RawSnapshot:
        """Fetch daily schedule/scoreboard page.

        URL pattern assumption: mykbostats.com/scores/YYYY-MM-DD
        This may need adjustment based on actual site structure.
        """
        date_str = target_date.strftime("%Y-%m-%d")
        url = f"{BASE_URL}/scores/{date_str}"
        return await self._fetch(url)

    async def fetch_game_detail(self, game_url: str) -> RawSnapshot:
        """Fetch single game detail page.

        Args:
            game_url: Full URL or relative path (e.g. /games/12345)
        """
        if game_url.startswith("http"):
            url = game_url
        else:
            url = f"{BASE_URL}{game_url}"
        return await self._fetch(url)
