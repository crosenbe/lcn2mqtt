"""Handler for LCN LED status outputs."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pypck import inputs, lcn_defs

from lcn2mqtt.handlers.dispatcher import input_handler, mqtt_handler
from lcn2mqtt.helpers import MqttMessage

from ..models.device import Device, LedState

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

    # fetch config
    keys = [
        button_config.table_a.keys if button_config.table_a else [False] * 8,
        button_config.table_b.keys if button_config.table_b else [False] * 8,
        button_config.table_c.keys if button_config.table_c else [False] * 8,
        button_config.table_d.keys if button_config.table_d else [False] * 8,
    ]
    commands = [
        button_config.table_a.command if button_config.table_a else lcn_defs.SendKeyCommand.DONTSEND,
        button_config.table_b.command if button_config.table_b else lcn_defs.SendKeyCommand.DONTSEND,
        button_config.table_c.command if button_config.table_c else lcn_defs.SendKeyCommand.DONTSEND,
        button_config.table_d.command if button_config.table_d else lcn_defs.SendKeyCommand.DONTSEND,
    ]

    # Inactive at the moment
    #await device_connection.send_keys(keys=keys, cmd=commands)
