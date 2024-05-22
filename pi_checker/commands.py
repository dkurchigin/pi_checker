from __future__ import annotations

import asyncio
import re

from pi_checker.results import Result


class BaseCommand:
    command: str
    result: Result | None = None
    is_success: bool = False
    error_message: str | None = None

    @classmethod
    def validate(cls) -> None:
        if cls.result.stdout == '':  # type: ignore
            cls.error_message = 'Stdout is Empty'
        else:
            cls.is_success = True

    @classmethod
    async def process_command(cls) -> Result:
        proc = await asyncio.create_subprocess_shell(
            cls.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()
        return Result(
            command=cls.command,
            stdout=stdout.decode(),
            stderr=stderr.decode(),
            return_code=proc.returncode,
        )

    @classmethod
    async def run(cls) -> None:
        try:
            cls.result = await cls.process_command()

            if cls.result is None:
                cls.error_message = 'Result is None'
            elif not cls.result.is_failed:
                cls.validate()
            else:
                cls.error_message = f'Error while execute command: {cls.result.stderr}'
        except Exception as exc:
            cls.error_message = f'Can\'t process or validate command: {str(exc)}'


class MeasureTemperature(BaseCommand):
    command = 'vcgencmd measure_temp'

    @classmethod
    def validate(cls) -> None:
        pattern = r'temp\=(\d+?\.\d+?).*?'
        matched_result = re.search(pattern=pattern, string=cls.result.stdout)  # type: ignore

        if matched_result is None:
            cls.error_message = 'Can\'t get measure temperature'
        else:
            value = float(matched_result.group(1))
            if value >= 60.0:
                cls.error_message = f'Measure temperature is too high: {value}'
            else:
                cls.is_success = True


class MeasureVoltage(BaseCommand):
    command = 'vcgencmd measure_volts'

    @classmethod
    def validate(cls) -> None:
        pattern = r'volt\=(\d+?\.\d+?)V'
        matched_result = re.search(pattern=pattern, string=cls.result.stdout)  # type: ignore

        if matched_result is None:
            cls.error_message = 'Can\'t get measure voltage'
        else:
            value = float(matched_result.group(1))
            if value <= 0.8 or value >= 1.35:
                cls.error_message = f'Measure voltage incorrect: {value}. Should be of 0.8V to 1.35V'
            else:
                cls.is_success = True


class DiskFree(BaseCommand):
    command = 'df -h'

    @classmethod
    def validate(cls) -> None:
        pattern = r'\/dev\/root.*?(\d+)%.*?\/'
        matched_result = re.search(pattern=pattern, string=cls.result.stdout)  # type: ignore

        if matched_result is None:
            cls.error_message = 'Can\'t get disk free'
        else:
            value = int(matched_result.group(1))
            if value >= 80.0:
                cls.error_message = f'Used disk space is too big: {value}%'
            else:
                cls.is_success = True
