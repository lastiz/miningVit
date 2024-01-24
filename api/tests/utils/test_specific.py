import pytest
from contextlib import nullcontext as does_not_raise

from src.utils.specific import gen_rand_alphanum_str


@pytest.mark.parametrize(
    "length, expectation",
    [
        (1, does_not_raise()),
        (4, does_not_raise()),
        (5, does_not_raise()),
        (36, does_not_raise()),
        (0, does_not_raise()),
        (37, pytest.raises(ValueError)),
        (123.545, pytest.raises(ValueError)),
    ],
)
def test_get_rand_alphanum_str(length, expectation):
    with expectation:
        res = gen_rand_alphanum_str(length)
        assert isinstance(res, str)
        assert length == len(res)
