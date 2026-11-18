"""ESPSomfy parent entity class."""

from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, VERSION
from .controller import ESPSomfyController
from .shade_devices import shade_device_info


class ESPSomfyEntity(CoordinatorEntity[ESPSomfyController], Entity):
    """Base entitly for the ESPSomfy controller."""

    def __init__(self, *, data: any, controller: ESPSomfyController) -> None:
        """Initialize the entity."""
        super().__init__(coordinator=controller)
        self.controller = controller

    @property
    def should_poll(self) -> bool:
        """Indicates that the entity should not poll."""
        return False

    @property
    def device_info(self) -> DeviceInfo | None:
        """Device info."""
        return DeviceInfo(
            configuration_url=self.controller.api.get_config_url(),
            identifiers={(DOMAIN, self.controller.unique_id)},
            name=self.controller.device_name,
            manufacturer=MANUFACTURER,
            model=f"ESPSomfy RTS Integration {VERSION}",
            sw_version=self.controller.version,
            hw_version=None,
        )


class ESPSomfyShadeEntity(ESPSomfyEntity):
    """Base entity for a shade or a group with equivalent controls."""

    def __init__(self, *, data: dict, controller: ESPSomfyController) -> None:
        """Initialize the entity with its shade or group data."""
        super().__init__(data=data, controller=controller)
        self._shade_device_data = data

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return the shade device, or the controller device for groups."""
        if "groupId" in self._shade_device_data:
            return super().device_info
        return shade_device_info(
            self.controller.unique_id,
            self._shade_device_data,
            self.controller.api.get_config_url(),
        )
