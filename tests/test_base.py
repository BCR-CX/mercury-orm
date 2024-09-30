import pytest
import requests
from mercuryfieldservice.client.connection import ZendeskAPIClient
from mercuryfieldservice import fields
from mercuryfieldservice.base import CustomObject


class MockCustomObject(CustomObject):
    name = fields.TextField("name")
    codigo = fields.TextField("codigo")
    ativo = fields.CheckboxField("ativo")


@pytest.fixture
def custom_object():
    return MockCustomObject(name="Test Object", codigo="1234", ativo=True)


def test_custom_object_creation(custom_object):
    # Testa a criação de um objeto CustomObject
    assert custom_object.name == "Test Object"
    assert custom_object.codigo == "1234"
    assert custom_object.ativo is True


def test__str__(custom_object):
    assert custom_object.__str__() == "MockCustomObject"


def test__repr__(custom_object):
    assert custom_object.__repr__()


def test_custom_object_to_dict(custom_object):
    result = custom_object.to_dict()
    expected_dict = {
        "name": "Test Object",
        "codigo": "1234",
        "ativo": True,
        # "id": None,
        # "created_at": None,
        # "updated_at": None,
        # "created_by_user_id": None,
        # "updated_by_user_id": None,
        # "external_id": None
    }
    assert result == expected_dict


def test_custom_object_save_create(requests_mock, custom_object):
    url = f"/custom_objects/{custom_object.__class__.__name__.lower()}/records"
    mock_response = {
        "custom_object_record": {
            "id": "1",
            "name": "Test Object",
            "custom_object_fields": {"codigo": "1234", "ativo": True},
        }
    }
    requests_mock.post(f"{ZendeskAPIClient().base_url}{url}", json=mock_response)

    response = custom_object.save()
    assert custom_object.id == "1"
    assert response["custom_object_record"]["id"] == "1"


def test_custom_object_save_update(requests_mock, custom_object):
    custom_object.id = "1"
    url = f"/custom_objects/{custom_object.__class__.__name__.lower()}/records/{custom_object.id}"
    mock_response = {
        "custom_object_record": {
            "id": "1",
            "name": "Updated Object",
            "custom_object_fields": {"codigo": "1234", "ativo": False},
        }
    }
    requests_mock.patch(f"{ZendeskAPIClient().base_url}{url}", json=mock_response)

    custom_object.name = "Updated Object"
    custom_object.ativo = False
    response = custom_object.save()
    assert custom_object.name == "Updated Object"
    assert custom_object.ativo is False
    assert response["custom_object_record"]["name"] == "Updated Object"


def test_custom_object_delete(requests_mock, custom_object):
    custom_object.id = "1"
    url = (
        f"/custom_objects/{custom_object.__class__.__name__}/records/{custom_object.id}"
    )
    requests_mock.delete(f"{ZendeskAPIClient().base_url}{url}", status_code=204)

    response_status = custom_object.delete()
    assert response_status == 204
