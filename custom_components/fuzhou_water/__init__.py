"""Fuzhou Water integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

import async_timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_URL,
    CONF_AUTHORIZATION,
    CONF_END_DATE,
    CONF_START_DATE,
    CONF_TOKEN,
    CONF_USER_NAME,
    CONF_USER_NO,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

PLATFORMS = ["sensor"]

LOGGER = logging.getLogger(__name__)


def _build_payload(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "actionType": "0029",
        "Token": config[CONF_TOKEN],
        "userNo": config[CONF_USER_NO],
        "userName": config[CONF_USER_NAME],
        "startDate": config[CONF_START_DATE],
        "endDate": config[CONF_END_DATE],
    }


async def _async_fetch_water_data(
    hass: HomeAssistant,
    config: dict[str, Any],
) -> dict[str, Any]:
    session = async_get_clientsession(hass)
    headers = {
        "Authorization": config[CONF_AUTHORIZATION],
        "Accept": "application/json",
        "Content-Type": "application/json;charset=UTF-8",
    }
    try:
        async with async_timeout.timeout(20):
            response = await session.post(API_URL, headers=headers, json=_build_payload(config))
        response.raise_for_status()
        data = await response.json()
    except Exception as err:  # pragma: no cover - network handling
        raise UpdateFailed(f"Unable to fetch water data: {err}") from err

    if data.get("result") != "1":
        raise UpdateFailed(data.get("msg", "Unexpected API response"))

    return data


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Fuzhou Water from a config entry."""
    coordinator = DataUpdateCoordinator[dict[str, Any]](
        hass,
        logger=LOGGER,
        name="Fuzhou Water",
        update_method=lambda: _async_fetch_water_data(hass, entry.data),
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unload_ok
