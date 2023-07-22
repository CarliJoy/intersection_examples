import pytest


base_types = (
    int,
    float,
    str,
    bytes,
    bytearray,
    bool,
    type,
    BaseException,
    set,
    list,
    tuple,
    range,
    memoryview,
    dict,
    frozenset,
    complex,
)


@pytest.mark.parametrize("a", base_types)
@pytest.mark.parametrize("b", base_types)
def test_types(a, b):
    """We are not allowed to mix basetypes in an MRO"""
    if a == b:
        return
    with pytest.raises(TypeError):
        type("foo", (a, b), {})
