"""Device registration for individual shades."""

from __future__ import annotations

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .const import DOMAIN, MANUFACTURER


def shade_device_info(
    controller_id: str, shade: dict, configuration_url: str
) -> dr.DeviceInfo:
    """Describe the device shared by a shade and its sensors and switches."""
    return dr.DeviceInfo(
        identifiers={(DOMAIN, f"{controller_id}_shade_{shade['shadeId']}")},
        name=shade["name"],
        manufacturer=MANUFACTURER,
        configuration_url=configuration_url,
    )


@callback
def async_relink_shade_entities(
    hass: HomeAssistant,
    config_entry_id: str,
    controller_id: str,
    shades: list[dict],
    configuration_url: str,
) -> None:
    """Move existing shade entities to their devices while retaining registry IDs."""
    entities = er.async_get(hass)
    existing = {
        (entry.domain, entry.unique_id): entry
        for entry in er.async_entries_for_config_entry(entities, config_entry_id)
        if entry.platform == DOMAIN
    }
    if not existing:
        return

    devices = dr.async_get(hass)
    for shade in shades:
        if "shadeId" not in shade or "name" not in shade:
            continue
        suffix = f"{controller_id}_{shade['shadeId']}"
        keys = (
            ("cover", suffix),
            ("binary_sensor", f"sun_{suffix}"),
            ("binary_sensor", f"wind_{suffix}"),
            ("switch", f"sunswitch_{suffix}"),
            ("switch", f"binaryswitch_{suffix}"),
        )
        entries = [existing[key] for key in keys if key in existing]
        if not entries:
            continue
        device = devices.async_get_or_create(
            config_entry_id=config_entry_id,
            **shade_device_info(controller_id, shade, configuration_url),
        )
        for entry in entries:
            if entry.device_id != device.id:
                entities.async_update_entity(entry.entity_id, device_id=device.id)
