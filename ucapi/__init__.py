#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration driver library for Remote Two.

:copyright: (c) 2023 by Unfolded Circle ApS.
:license: MPL-2.0, see LICENSE for more details.
"""

# Set default logging handler to avoid "No handler found" warnings.
import logging  # isort:skip

from .api_definitions import DeviceStates, Events, StatusCodes  # isort:skip # noqa: F401
from .entity import Entity, EntityTypes  # isort:skip # noqa: F401
from .entities import Entities  # isort:skip # noqa: F401
from .api import IntegrationAPI  # isort:skip # noqa: F401

# Entity types
from .button import Button  # noqa: F401
from .climate import Climate  # noqa: F401
from .cover import Cover  # noqa: F401
from .light import Light  # noqa: F401
from .media_player import MediaPlayer  # noqa: F401
from .sensor import Sensor  # noqa: F401
from .switch import Switch  # noqa: F401

logging.getLogger(__name__).addHandler(logging.NullHandler())
