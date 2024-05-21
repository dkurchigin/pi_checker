from __future__ import annotations

from typing import Type
from enum import Enum

from pi_checker.commands import BaseCommand


class CheckType(str, Enum):
    warning = 'WARNING'
    error = 'ERROR'


class BaseRunner:
    type: CheckType = CheckType.warning
    error_message: str | None = None

    @classmethod
    async def get_result(cls, command_class: Type[BaseCommand]):
        await command_class.run()
