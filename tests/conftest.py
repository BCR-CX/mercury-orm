import pytest
import requests_mock
from unittest.mock import patch
from mercuryfieldservice.client.zendesk_manager import ZendeskObjectManager
from mercuryfieldservice.client.connection import ZendeskAPIClient
from mercuryfieldservice.record_manager import RecordManager
from mercuryfieldservice import fields


@pytest.fixture
def zendesk_client(monkeypatch):
    with patch.object(ZendeskAPIClient, "__init__", return_value=None):
        client = ZendeskAPIClient()
        client.base_url = "https://mocked-subdomain.zendesk.com/api/v2"
        client.auth = None
        client.headers = {"Content-Type": "application/json"}
        yield client


@pytest.fixture
def zendesk_object_manager():
    with patch.object(ZendeskAPIClient, "__init__", return_value=None):
        manager = ZendeskObjectManager()
        manager.client.base_url = "https://mocked-subdomain.zendesk.com/api/v2"
        manager.client.headers = {"Content-Type": "application/json"}
        manager.client.auth = None
        yield manager


@pytest.fixture
def custom_object():
    class MockCustomObject:
        def __init__(self, name, codigo, ativo):
            self.name = name
            self.codigo = codigo
            self.ativo = ativo
            self.id = None

        def __str__(self):
            return self.__class__.__name__

        def save(self):
            data = {
                "custom_object_record": {
                    "id": "1",
                    "name": self.name,
                    "custom_object_fields": {
                        "codigo": self.codigo,
                        "ativo": self.ativo,
                    },
                }
            }
            self.id = data["custom_object_record"]["id"]
            return data

        def to_dict(self):
            return {
                "id": self.id,
                "name": self.name,
                "codigo": self.codigo,
                "ativo": self.ativo,
            }

        def delete(self):
            if self.id:
                return 204
            return {"error": "Object does not exist"}

    return MockCustomObject(name="Test Object", codigo="1234", ativo=True)


class MockModel:
    name = fields.TextField("name")
    codigo = fields.TextField("codigo")
    ativo = fields.CheckboxField("ativo")


@pytest.fixture
def record_manager():
    return RecordManager(model=MockModel)
