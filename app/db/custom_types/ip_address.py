from __future__ import annotations

import ipaddress
from typing import Optional

from sqlalchemy import types


class IPv4Address(types.TypeDecorator):
    impl = types.String(15)

    def process_bind_param(
        self, value: Optional[ipaddress.IPv4Address], dialect: Dialect
    ) -> Optional[str]:
        return value and str(value)

    def process_result_value(
        self, value: Optional[str], dialect: Dialect
    ) -> Optional[ipaddress.IPv4Address]:
        return value and ipaddress.IPv4Address(value)
