import pydantic

from techcable.orderedset import OrderedSet


def test_deser_orderedset() -> None:
    raw_data = [1, 2, 7, 8, 9, 1]
    res = pydantic.TypeAdapter(OrderedSet[int]).validate_python(raw_data)
    assert isinstance(res, OrderedSet)
    assert res == OrderedSet(raw_data)
    res = pydantic.TypeAdapter(OrderedSet[int]).validate_json("[1,2,7,8,9,1]")
    assert res == OrderedSet(raw_data)


def test_ser_orderedset() -> None:
    raw_data = [1, 2, 7, 8, 9, 1]
    oset = OrderedSet(raw_data)
    ser = pydantic.TypeAdapter(OrderedSet[int]).dump_python(oset)
    assert isinstance(ser, list)
    assert ser == list(OrderedSet(raw_data))
