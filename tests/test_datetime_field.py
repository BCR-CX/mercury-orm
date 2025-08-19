from datetime import datetime, timezone

import pytest

from mercuryorm.fields import DateTimeField, IntegerField
from mercuryorm.base import CustomObject


class DateTeste(CustomObject):
    ticket_id = IntegerField("ticket_id")
    created_at = DateTimeField("created_at")
    updated_at = DateTimeField("updated_at")


@pytest.fixture
def dateteste_zendesk():
    return {
        "id": 1,
        "name": "Test Date Object",
        "custom_object_fields": {
            "ticket_id": 1,
            "created_at": "2023-07-15",
            "created_at_time": "10:30:45.187652+00:00",
            "updated_at": "2023-07-16",
            "updated_at_time": "15:20:33.187652+00:00",
        },
    }


@pytest.fixture
def dateteste_get_response_mock(requests_mock, dateteste_zendesk):
    date_obj = {"custom_object_record": dateteste_zendesk}
    requests_mock.get(
        "https://mockdomain.zendesk.com/api/v2/custom_objects/dateteste/records/1",
        json=date_obj,
    )
    return dateteste_zendesk


@pytest.fixture
def dateteste_all_response_mock(requests_mock, dateteste_zendesk):
    dates = {"custom_object_records": [dateteste_zendesk]}
    requests_mock.get(
        "https://mockdomain.zendesk.com/api/v2/custom_objects/dateteste/records",
        json=dates,
    )
    return dates


@pytest.fixture
def dateteste_create_response_mock(requests_mock, dateteste_zendesk):
    date_obj = {"custom_object_record": dateteste_zendesk}
    requests_mock.post(
        "https://mockdomain.zendesk.com/api/v2/custom_objects/dateteste/records",
        json=date_obj,
    )
    return date_obj


def test_datetime_field_response_type_none():
    teste = DateTeste()
    assert teste.created_at is None
    assert teste.updated_at is None


def test_datetime_field_get(dateteste_get_response_mock):
    date_obj = DateTeste.objects.get(id=1)
    assert isinstance(date_obj.created_at, datetime)
    assert date_obj.created_at.year == 2023
    assert date_obj.created_at.month == 7
    assert date_obj.created_at.day == 15
    assert date_obj.created_at.hour == 10
    assert date_obj.created_at.minute == 30
    assert date_obj.created_at.second == 45

    assert isinstance(date_obj.updated_at, datetime)
    assert date_obj.updated_at.year == 2023
    assert date_obj.updated_at.month == 7
    assert date_obj.updated_at.day == 16
    assert date_obj.updated_at.hour == 15
    assert date_obj.updated_at.minute == 20
    assert date_obj.updated_at.second == 33


def test_datetime_field_all(dateteste_all_response_mock, dateteste_zendesk):
    date_objs = DateTeste.objects.all()
    date_obj = date_objs[0]

    assert isinstance(date_obj.created_at, datetime)
    assert (
        date_obj.created_at.isoformat()
        == f"{dateteste_zendesk['custom_object_fields']['created_at']}T{dateteste_zendesk['custom_object_fields']['created_at_time']}"
    )
    assert (
        date_obj.updated_at.isoformat()
        == f"{dateteste_zendesk['custom_object_fields']['updated_at']}T{dateteste_zendesk['custom_object_fields']['updated_at_time']}"
    )


def test_datetime_field_save(dateteste_create_response_mock):
    date_obj = DateTeste(ticket_id=1)
    date_obj.created_at = datetime(2023, 7, 15, 10, 30, 45, tzinfo=timezone.utc)
    date_obj.updated_at = datetime(2023, 7, 16, 15, 20, 33, tzinfo=timezone.utc)
    date_obj.save()

    assert date_obj.created_at.isoformat() == "2023-07-15T10:30:45+00:00"
    assert date_obj.updated_at.isoformat() == "2023-07-16T15:20:33+00:00"


def test_datetime_field_string_assignment(dateteste_create_response_mock):
    date_obj = DateTeste(ticket_id=1)
    date_obj.created_at = datetime.strptime(
        "2023-07-15T10:30:45Z", "%Y-%m-%dT%H:%M:%SZ"
    )
    date_obj.updated_at = datetime.strptime(
        "2023-07-16T15:20:33Z", "%Y-%m-%dT%H:%M:%SZ"
    )
    date_obj.save()

    assert isinstance(date_obj.created_at, datetime)
    assert date_obj.created_at.year == 2023
    assert date_obj.created_at.month == 7
    assert date_obj.created_at.day == 15

    assert isinstance(date_obj.updated_at, datetime)
    assert date_obj.updated_at.hour == 15
    assert date_obj.updated_at.minute == 20
