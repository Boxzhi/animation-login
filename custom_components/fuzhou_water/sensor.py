"""Sensor platform for Fuzhou Water."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN


@dataclass(frozen=True, kw_only=True)
class FuzhouWaterSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any] | None], Any]


def _latest_record(data: dict[str, Any] | None) -> dict[str, Any] | None:
    if not data:
        return None
    records = data.get("data") or []
    if not records:
        return None
    return sorted(records, key=lambda item: item.get("cbny", ""), reverse=True)[0]


def _latest_bill_amount(data: dict[str, Any] | None) -> Any:
    record = _latest_record(data)
    return None if record is None else record.get("jfje")


def _latest_usage(data: dict[str, Any] | None) -> Any:
    record = _latest_record(data)
    return None if record is None else record.get("fbysl")


def _arrears_amount(data: dict[str, Any] | None) -> Any:
    record = _latest_record(data)
    return None if record is None else record.get("qfje")


SENSOR_DESCRIPTIONS: tuple[FuzhouWaterSensorDescription, ...] = (
    FuzhouWaterSensorDescription(
        key="latest_bill_amount",
        name="Latest Bill Amount",
        native_unit_of_measurement="CNY",
        device_class=SensorDeviceClass.MONETARY,
        value_fn=_latest_bill_amount,
    ),
    FuzhouWaterSensorDescription(
        key="latest_usage",
        name="Latest Usage",
        native_unit_of_measurement="m³",
        value_fn=_latest_usage,
    ),
    FuzhouWaterSensorDescription(
        key="arrears_amount",
        name="Arrears Amount",
        native_unit_of_measurement="CNY",
        device_class=SensorDeviceClass.MONETARY,
        value_fn=_arrears_amount,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        FuzhouWaterSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class FuzhouWaterSensor(CoordinatorEntity[DataUpdateCoordinator], SensorEntity):
    """Representation of a Fuzhou Water sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        description: FuzhouWaterSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=f"{self._entry.title} Water",
            manufacturer="Fuzhou Public Water",
        )

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        record = _latest_record(self.coordinator.data)
        if not record:
            return None
        return {
            "billing_month": record.get("cbny"),
            "read_date": record.get("cbrq"),
            "start_reading": record.get("sccjs"),
            "end_reading": record.get("bccjs"),
            "paid_date": record.get("sfrq"),
            "user_name": record.get("yhmc"),
            "user_no": record.get("yhbh"),
            "address": record.get("yhdz"),
        }
