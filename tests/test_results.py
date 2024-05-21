import pytest

from tests.data_factory.result import ResultFactory


@pytest.mark.parametrize(
    'stderr, return_code, is_failed_expected',
    [
        ('', 0, False),
        ('boom', 0, True),
        ('', 1, True),
        ('boom', 1, True),
    ]
)
def test_result_is_failed(stderr, return_code, is_failed_expected):
    result = ResultFactory.create(stderr=stderr, return_code=return_code)
    assert result.is_failed == is_failed_expected
