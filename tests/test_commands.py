from unittest.mock import AsyncMock, patch

import pytest

from pi_checker.commands import DiskFree, MeasureTemperature, MeasureVoltage
from pi_checker.runners import BaseCommand
from tests.data_factory.result import ResultFactory


@pytest.mark.parametrize(
    'stdout, expected_error_message, expected_is_success',
    [
        ('', 'Stdout is Empty', False),
        ('Success, Bro', None, True),
    ]
)
def test_base_command_validate(stdout, expected_error_message, expected_is_success):
    class MockedCommand(BaseCommand):
        result = ResultFactory.create(stdout=stdout)

    MockedCommand.validate()
    assert MockedCommand.is_success == expected_is_success
    assert MockedCommand.error_message == expected_error_message


@pytest.mark.parametrize(
    'stdout, expected_error_message, expected_is_success',
    [
        ('', 'Can\'t get measure temperature', False),
        ('Success, Bro?', 'Can\'t get measure temperature', False),
        ('temp=38.6\'C', None, True),
        ('temp=60.0\'C', 'Measure temperature is too high: 60.0', False),
        ('temp=.0\'C', 'Can\'t get measure temperature', False),
    ]
)
def test_measure_temperature_validate(stdout, expected_error_message, expected_is_success):
    class MockedCommand(MeasureTemperature):
        result = ResultFactory.create(stdout=stdout)

    MockedCommand.validate()
    assert MockedCommand.is_success == expected_is_success
    assert MockedCommand.error_message == expected_error_message


@pytest.mark.parametrize(
    'stdout, expected_error_message, expected_is_success',
    [
        ('', 'Can\'t get measure voltage', False),
        ('Success, Bro?', 'Can\'t get measure voltage', False),
        ('volt=1.3312V', None, True),
        ('volt=0.7V', 'Measure voltage incorrect: 0.7. Should be of 0.8V to 1.35V', False),
        ('volt=1.419V', 'Measure voltage incorrect: 1.419. Should be of 0.8V to 1.35V', False),
        ('volt=.0V', 'Can\'t get measure voltage', False),
    ]
)
def test_measure_voltage_validate(stdout, expected_error_message, expected_is_success):
    class MockedCommand(MeasureVoltage):
        result = ResultFactory.create(stdout=stdout)

    MockedCommand.validate()
    assert MockedCommand.is_success == expected_is_success
    assert MockedCommand.error_message == expected_error_message


@pytest.mark.parametrize(
    'stdout, expected_error_message, expected_is_success',
    [
        ('', 'Can\'t get disk free', False),
        ('Success, Bro?', 'Can\'t get disk free', False),
        (
            """
            Filesystem      Size  Used Avail Use% Mounted on
            /dev/root        15G  3.6G   11G  26% /
            devtmpfs        333M     0  333M   0% /dev
            tmpfs           461M     0  461M   0% /dev/shm
            tmpfs           185M  1.1M  184M   1% /run
            tmpfs           5.0M  4.0K  5.0M   1% /run/lock
            /dev/mmcblk0p1  255M   51M  205M  20% /boot
            tmpfs            93M   20K   93M   1% /run/user/1000
            """, None, True
        ),
        (
            """
            Filesystem      Size  Used Avail Use% Mounted on
            /dev/root        15G  3.6G   11G  89% /
            devtmpfs        333M     0  333M   0% /dev
            tmpfs           461M     0  461M   0% /dev/shm
            tmpfs           185M  1.1M  184M   1% /run
            tmpfs           5.0M  4.0K  5.0M   1% /run/lock
            /dev/mmcblk0p1  255M   51M  205M  20% /boot
            tmpfs            93M   20K   93M   1% /run/user/1000
            """, 'Used disk space is too big: 89%', False
        ),
        (
            """
            Filesystem      Size  Used Avail Use% Mounted on
            /dev/        15G  3.6G   11G  89% /
            devtmpfs        333M     0  333M   0% /dev
            tmpfs           461M     0  461M   0% /dev/shm
            tmpfs           185M  1.1M  184M   1% /run
            tmpfs           5.0M  4.0K  5.0M   1% /run/lock
            /dev/mmcblk0p1  255M   51M  205M  20% /boot
            tmpfs            93M   20K   93M   1% /run/user/1000
            """, 'Can\'t get disk free', False
        ),
    ]
)
def test_disk_free_validate(stdout, expected_error_message, expected_is_success):
    class MockedCommand(DiskFree):
        result = ResultFactory.create(stdout=stdout)

    MockedCommand.validate()
    assert MockedCommand.is_success == expected_is_success
    assert MockedCommand.error_message == expected_error_message


@pytest.mark.asyncio
@patch('pi_checker.commands.BaseCommand.process_command')
@pytest.mark.parametrize(
    'command_class', [BaseCommand, MeasureTemperature, MeasureVoltage, DiskFree]
)
async def test_command_run_without_result(process_command_mock: AsyncMock, command_class):
    class MockedCommand(command_class):
        ...

    process_command_mock.return_value = None
    await MockedCommand.run()
    assert MockedCommand.error_message == 'Result is None'


@pytest.mark.asyncio
@patch('pi_checker.commands.BaseCommand.process_command')
@pytest.mark.parametrize(
    'command_class', [BaseCommand, MeasureTemperature, MeasureVoltage, DiskFree]
)
async def test_command_run_with_exception(process_command_mock: AsyncMock, command_class):
    class MockedCommand(command_class):
        ...

    exc = ValueError('some exc')
    process_command_mock.side_effect = exc
    await MockedCommand.run()
    assert MockedCommand.error_message == f'Can\'t process or validate command: {str(exc)}'


@pytest.mark.asyncio
@patch('pi_checker.commands.BaseCommand.process_command')
@pytest.mark.parametrize(
    'command_class', [BaseCommand, MeasureTemperature, MeasureVoltage, DiskFree]
)
async def test_command_run_with_failed_result(process_command_mock: AsyncMock, command_class):
    class MockedCommand(command_class):
        ...

    process_command_mock.return_value = ResultFactory.create(stderr='some error', return_code=1)
    await MockedCommand.run()
    assert MockedCommand.error_message == 'Error while execute command: some error'


@pytest.mark.asyncio
@patch('pi_checker.commands.BaseCommand.process_command')
@pytest.mark.parametrize(
    'command_class, stdout', [
        (BaseCommand, 'Success, Bro'),
        (MeasureTemperature, 'temp=38.6\'C'),
        (MeasureVoltage, 'volt=1.3312V'),
        (
            DiskFree, """
                Filesystem      Size  Used Avail Use% Mounted on
                /dev/root        15G  3.6G   11G  26% /
                devtmpfs        333M     0  333M   0% /dev
                tmpfs           461M     0  461M   0% /dev/shm
                tmpfs           185M  1.1M  184M   1% /run
                tmpfs           5.0M  4.0K  5.0M   1% /run/lock
                /dev/mmcblk0p1  255M   51M  205M  20% /boot
                tmpfs            93M   20K   93M   1% /run/user/1000
            """
        )
    ]
)
async def test_command_run_with_result(process_command_mock: AsyncMock, command_class, stdout):
    class MockedCommand(command_class):
        ...

    process_command_mock.return_value = ResultFactory.create(stdout=stdout, stderr='', return_code=0)
    await MockedCommand.run()
    assert MockedCommand.is_success is True
