"""Config flow for Fuzhou Water integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    API_URL,
    CONF_AUTHORIZATION,
    CONF_END_DATE,
    CONF_START_DATE,
    CONF_TOKEN,
    CONF_USER_NAME,
    CONF_USER_NO,
    DOMAIN,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_AUTHORIZATION): str,
        vol.Required(CONF_TOKEN): str,
        vol.Required(CONF_USER_NO): str,
        vol.Required(CONF_USER_NAME): str,
        vol.Required(CONF_START_DATE): str,
        vol.Required(CONF_END_DATE): str,
    }
)


async def _async_validate_input(hass: HomeAssistant, data: dict[str, str]) -> None:
    session = async_get_clientsession(hass)
    headers = {
        "Authorization": data[CONF_AUTHORIZATION],
        "Accept": "application/json",
        "Content-Type": "application/json;charset=UTF-8",
    }
    payload = {
        "actionType": "0029",
        "Token": data[CONF_TOKEN],
        "userNo": data[CONF_USER_NO],
        "userName": data[CONF_USER_NAME],
        "startDate": data[CONF_START_DATE],
        "endDate": data[CONF_END_DATE],
    }
    response = await session.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    body = await response.json()
    if body.get("result") != "1":
        raise ValueError(body.get("msg", "Unknown error"))


class FuzhouWaterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fuzhou Water."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, str] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await _async_validate_input(self.hass, user_input)
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=f"{user_input[CONF_USER_NAME]} {user_input[CONF_USER_NO]}",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
