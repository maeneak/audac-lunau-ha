"""Constants for the Audac Luna-U integration."""
from __future__ import annotations

DOMAIN = "audac_luna_u"

DEFAULT_PORT = 5001
DEFAULT_ADDRESS = 1
DEFAULT_ZONES = 8
DEFAULT_INPUTS = 8
DEFAULT_GPO_COUNT = 12
DEFAULT_POLL_INTERVAL = 10  # seconds

CONF_ADDRESS = "address"
CONF_ZONES = "zones"
CONF_INPUTS = "inputs"
CONF_GPO_COUNT = "gpo_count"
CONF_POLL_INTERVAL = "poll_interval"

DATA_CLIENT = "client"
DATA_COORDINATOR = "coordinator"
