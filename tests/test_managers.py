import pytest
import requests
from mercuryorm.client.connection import ZendeskAPIClient
from mercuryorm.managers import QuerySet


class MockModel:
    __name__ = "MockModel"

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def queryset():
    return QuerySet(model=MockModel)


def test_all_records(queryset, requests_mock):
    url = f"/custom_objects/{queryset.model.__name__.lower()}/records"
    mock_response = {
        "custom_object_records": [
            {
                "id": "1",
                "name": "Record 1",
                "custom_object_fields": {"field1": "value1"},
            },
            {
                "id": "2",
                "name": "Record 2",
                "custom_object_fields": {"field2": "value2"},
            },
        ]
    }
    requests_mock.get(f"{ZendeskAPIClient().base_url}{url}", json=mock_response)

    records = queryset.all()
    assert len(records) == 2
    assert records[0].id == "1"
    assert records[1].id == "2"


def test_all_with_pagination(queryset, requests_mock):
    url = f"/custom_objects/{queryset.model.__name__.lower()}/records"
    mock_response = {
        "custom_object_records": [
            {
                "id": "1",
                "name": "Record 1",
                "custom_object_fields": {"field1": "value1"},
            }
        ],
        "meta": {"page_size": 1},
        "links": {"next": "next_url"},
    }
    requests_mock.get(f"{ZendeskAPIClient().base_url}{url}", json=mock_response)

    records, meta, links = queryset.all_with_pagination(page_size=1)

    assert len(records) == 1
    assert records[0].id == "1"
    assert meta["page_size"] == 1
    assert links["next"] == "next_url"


def test_filter_records(queryset, requests_mock):
    url = f"/custom_objects/{queryset.model.__name__.lower()}/records"
    mock_response = {
        "custom_object_records": [
            {
                "id": "1",
                "name": "Record 1",
                "custom_object_fields": {"field1": "value1"},
            },
            {
                "id": "2",
                "name": "Record 2",
                "custom_object_fields": {"field1": "value2"},
            },
        ]
    }
    requests_mock.get(f"{ZendeskAPIClient().base_url}{url}", json=mock_response)

    records = queryset.filter(field1="value1")

    assert len(records) == 1
    assert records[0].id == "1"
    assert records[0].field1 == "value1"


def test_parse_response(queryset):
    response_data = {
        "custom_object_records": [
            {
                "id": "1",
                "name": "Record 1",
                "custom_object_fields": {"field1": "value1"},
            },
            {
                "id": "2",
                "name": "Record 2",
                "custom_object_fields": {"field2": "value2"},
            },
        ]
    }

    records = queryset._parse_response(response_data)
    assert len(records) == 2
    assert records[0].id == "1"
    assert records[1].id == "2"


def test_parse_record_fields(queryset):
    record_data = {
        "id": "1",
        "name": "Record 1",
        "custom_object_fields": {"field1": "value1"},
        "created_at": "2024-09-29T08:02:57Z",
        "updated_at": "2024-09-29T08:03:57Z",
        "created_by_user_id": "user123",
        "updated_by_user_id": "user456",
        "external_id": None,
    }

    record = queryset.parse_record_fields(record_data)
    assert record.id == "1"
    assert record.name == "Record 1"
    assert record.field1 == "value1"
    assert record.created_at == "2024-09-29T08:02:57Z"
    assert record.updated_by_user_id == "user456"


def test_all_with_pagination_after_cursor(queryset, requests_mock):
    url = f"/custom_objects/{queryset.model.__name__.lower()}/records"
    mock_response = {
        "custom_object_records": [
            {
                "id": "3",
                "name": "Record 3",
                "custom_object_fields": {"field1": "value1"},
            }
        ],
        "meta": {"page_size": 1},
        "links": {"next": "next_url"},
    }
    requests_mock.get(f"{ZendeskAPIClient().base_url}{url}", json=mock_response)

    records, meta, links = queryset.all_with_pagination(
        page_size=1, after_cursor="abc123"
    )

    assert len(records) == 1
    assert records[0].id == "3"
    assert meta["page_size"] == 1
    assert links["next"] == "next_url"
