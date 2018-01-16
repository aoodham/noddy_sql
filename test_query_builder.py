import pytest
from datetime import datetime
from column import (Integer, String, DateTime, InvalidTypeError,
        InvalidOperation)
from query_builder import WebRating

@pytest.mark.parametrize('columnType, expected', [
    (Integer(), [1, 2, 3]),
    (String(), ["'1'", "'2'", "'3'"]),
    ])
def test_column_types_handle_lists(columnType, expected):
    value = [1, 2, 3]
    coerced = columnType.coerce(value)
    assert coerced == expected

def test_datetime_with_lists():
    value = ["2014-11-10", "2014-11-09", "2014-11-08"]
    coerced =  DateTime().coerce(value)
    assert coerced == ["'{}'".format(datetime(year=2014, month=11, day=10).isoformat()),
                       "'{}'".format(datetime(year=2014, month=11, day=9).isoformat()),
                       "'{}'".format(datetime(year=2014, month=11, day=8).isoformat())]

def test_query_method_creates_query_instance():
    query = WebRating.query()
    assert query.columns
    assert query.table is WebRating


@pytest.mark.parametrize('operand, value, expected',[
    ('__eq__', 2, 'id = 2'),
    ('__gt__', 2, 'id > 2'),
    ('__lt__', 2, 'id < 2'),
    ('in_', [1, 2], 'id in (1, 2)'),
    ('notIn', [1, 2], 'id not in (1, 2)'),
    ])
def test_operators(operand, value, expected):
    operator = getattr(WebRating.id, operand)(value)
    query = WebRating.query().filter(operator)
    assert query.toSQL() == "{} WHERE {};".format(
            query.base_string.format(WebRating.table_name),
            expected)

def test_can_build_range():
    r = 2 < WebRating.id < 3
    assert len(r) == 2
    assert r[0].value == 2
    assert r[1].value == 3
    #Clean up after test
    WebRating.id.reset()

def test_can_chain_multiple_calls_together():
    query = (WebRating.query()
            .filter(WebRating.id==1)
            .filter(WebRating.url=='http://somewhere.com'))
    assert query.toSQL() == "{} WHERE id = 1 AND url = 'http://somewhere.com';".format(
            query.base_string.format(WebRating.table_name)
    )

@pytest.mark.parametrize('input_time, expected', [
    ('2014-11-11', "'2014-11-11T00:00:00'"),
    ('2114-11-11 11:11:11', "'2114-11-11T11:11:11'"),
    (datetime(year=2014, month=11, day=11, hour=11, minute=1, second=0),
        "'2014-11-11T11:01:00'"),
])
def test_date_time_coercion(input_time, expected):
    dateTimeType = DateTime()
    formatted_time = dateTimeType.coerce(input_time)
    assert formatted_time == expected

def test_passing_a_string_to_an_integer_column():
    with pytest.raises(InvalidTypeError) as err:
        WebRating.query().filter(WebRating.id == 'some string')
    assert err.value.message == "invalid literal for int() with base 10: 'some string'"

def test_passing_non_date_string_to_datetime_column():
    with pytest.raises(InvalidTypeError) as err:
        WebRating.query().filter(WebRating.date == 'some string')
    assert err.value.message == 'Unknown string format'

def test_error_for_lt_on_string_field():
    with pytest.raises(InvalidOperation) as err:
        WebRating.query().filter(WebRating.url < 'some string')
    assert err.value.message == "Unsupported operand 'less'"

def test_error_for_gt_on_string_field():
    with pytest.raises(InvalidOperation) as err:
        WebRating.query().filter(WebRating.url > 'some string')
    assert err.value.message == "Unsupported operand 'greater'"


