"""Handler for LCN LED status outputs."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pypck import lcn_defs

from lcn2mqtt.handlers.dispatcher import mqtt_handler

from ..models.device import Device

_LOG = logging.getLogger(__name__)


if TYPE_CHECKING:
    from lcn2mqtt.bridge import Bridge


@mqtt_handler("sendkeys/+/set")
async def handle_command(
    subtopic: str, payload: str, module: Device, bridge: Bridge
) -> None:
    """Handle a sendkeys command ."""
    device_connection = module.device_connection

    parts = subtopic.split("/")
    try:
        button_identifier = parts[1]
    except ValueError:
        return

    # find device configuration
    try:
        device_config = bridge.config.devices[module.address]
        button_config = device_config.homeassistant.buttons[button_identifier]
    except KeyError:
        _LOG.warning("Unknown sendkeys button %r", button_identifier)
        return

    for idx, table in enumerate(
        [
            button_config.table_a,
            button_config.table_b,
            button_config.table_c,
            button_config.table_d,
        ]
    ):
        if table is not None:
            command = lcn_defs.SendKeyCommand[table.command.upper()]
            keys: list[list[bool]] = []
            for _ in range(idx):
                keys.append([False] * 8)
            keys.append(table.keys)
            for _ in range(3 - idx):
                keys.append([False] * 8)
            await device_connection.send_keys(keys=keys, cmd=command)
