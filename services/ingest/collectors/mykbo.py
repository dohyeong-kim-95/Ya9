"""myKBO Stats collector.

Fetches rendered HTML from mykbostats.com using Playwright (headless browser).
The site is JS-rendered with bot protection, so plain httpx requests get 403.

Falls back to httpx for the legacy site if Playwright is unavailable.

URL patterns (confirmed via research):
- Schedule: https://mykbostats.com/schedule/week_of/{YYYY-MM-DD}
- Game detail: https://mykbostats.com/games/{numeric_id}
- Legacy schedule: https://legacy.mykbostats.com/games/week_of/{YYYY-MM-DD}
"""

from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime
from typing import Optional

from ..models import CollectorError, RawSnapshot
from .base import BaseCollector

logger = logging.getLogger(__name__)

BASE_URL = "https://mykbostats.com"
LEGACY_BASE_URL = "https://legacy.mykbostats.com"

# Page load timeout
PAGE_TIMEOUT = 20_000  # ms


class MykboCollector(BaseCollector):
    """Collector for mykbostats.com using Playwright headless browser.

    The site is JS-rendered and blocks plain HTTP requests (403).
    Playwright renders the full page including dynamic content.

    Falls back to legacy.mykbostats.com via httpx if Playwright fails to launch.
    """

    def __init__(self, use_legacy: bool = False) -> None:
        self._browser = None
        self._playwright = None
        self._use_legacy = use_legacy
        self._initialized = False

    async def _ensure_browser(self) -> None:
        """Lazily start Playwright browser."""
        if self._initialized:
            return

        try:
            from playwright.async_api import async_playwright

            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            self._initialized = True
            logger.info("Playwright browser launched successfully")
        except Exception as e:
            logger.warning(
                "Playwright unavailable (%s), falling back to legacy httpx mode", e
            )
            self._use_legacy = True
            self._initialized = True

    async def close(self) -> None:
        """Clean up browser resources."""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def _fetch_with_playwright(self, url: str) -> RawSnapshot:
        """Fetch a page using Playwright headless browser."""
        await self._ensure_browser()

        if self._use_legacy or not self._browser:
            return await self._fetch_with_httpx(url)

        page = None
        try:
            page = await self._browser.new_page()
            await page.set_extra_http_headers({
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8",
            })

            resp = await page.goto(url, wait_until="networkidle", timeout=PAGE_TIMEOUT)
            if not resp:
                raise CollectorError(url=url, status_code=None, message="No response")

            status = resp.status
            html = await page.content()

            if status != 200:
                raise CollectorError(
                    url=url, status_code=status, message=f"HTTP {status}"
                )

            return RawSnapshot(
                url=url,
                html=html,
                fetched_at=datetime.now(),
                status_code=status,
            )
        except CollectorError:
            raise
        except Exception as e:
            raise CollectorError(url=url, status_code=None, message=str(e))
        finally:
            if page:
                await page.close()

    async def _fetch_with_httpx(self, url: str) -> RawSnapshot:
        """Fallback: fetch via httpx (for legacy site or when Playwright unavailable)."""
        import httpx

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
                "Mobile/15E148 Safari/604.1"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        try:
            async with httpx.AsyncClient(
                headers=headers, timeout=15.0, follow_redirects=True
            ) as client:
                resp = await client.get(url)
                if resp.status_code != 200:
                    raise CollectorError(
                        url=url,
                        status_code=resp.status_code,
                        message=f"HTTP {resp.status_code}",
                    )
                return RawSnapshot(
                    url=url,
                    html=resp.text,
                    fetched_at=datetime.now(),
                    status_code=resp.status_code,
                )
        except httpx.TimeoutException:
            raise CollectorError(url=url, status_code=None, message="Timeout")
        except httpx.HTTPError as e:
            raise CollectorError(url=url, status_code=None, message=str(e))

    async def fetch_game_list(self, target_date: date) -> RawSnapshot:
        """Fetch weekly schedule page containing the target date.

        Main site: https://mykbostats.com/schedule/week_of/{YYYY-MM-DD}
        Legacy:    https://legacy.mykbostats.com/games/week_of/{YYYY-MM-DD}
        """
        date_str = target_date.strftime("%Y-%m-%d")
        if self._use_legacy:
            url = f"{LEGACY_BASE_URL}/games/week_of/{date_str}"
        else:
            url = f"{BASE_URL}/schedule/week_of/{date_str}"
        return await self._fetch_with_playwright(url)

    async def fetch_game_detail(self, game_url: str) -> RawSnapshot:
        """Fetch single game detail page.

        Args:
            game_url: Full URL or numeric game ID or path like /games/12345
        """
        if game_url.startswith("http"):
            url = game_url
        elif game_url.isdigit():
            base = LEGACY_BASE_URL if self._use_legacy else BASE_URL
            url = f"{base}/games/{game_url}"
        else:
            base = LEGACY_BASE_URL if self._use_legacy else BASE_URL
            url = f"{base}{game_url}"
        return await self._fetch_with_playwright(url)
