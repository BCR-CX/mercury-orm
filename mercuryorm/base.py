"""
Module for handling CustomObject base functionality, including saving, deleting,
and managing fields for integration with Zendesk API.
"""

from mercuryorm import fields
from mercuryorm.client.connection import ZendeskAPIClient
from mercuryorm.exceptions import (
    CreateRecordError,
    DeleteRecordError,
    UniqueConstraintError,
    UpdateRecordError,
)
from mercuryorm.record_manager import RecordManager


class CustomObject:
    """
    A base class for custom objects that are synchronized with the Zendesk API.

    Provides methods for saving, deleting, and converting the object to a dictionary
    format for API communication. Automatically assigns a RecordManager to child classes.
    """

    def __init_subclass__(cls, **kwargs):
        """
        This method is called automatically whenever a subclass of CustomObject is created.
        It automatically assigns the RecordManager to the child class,
        without the need to define 'objects' manually.
        """
        super().__init_subclass__(**kwargs)
        cls.objects = RecordManager(cls)

    def __init__(self, **kwargs):
        self.client = ZendeskAPIClient()
        self.id = None  # pylint: disable=invalid-name
        self.name = None
        for field_name, field in self.__class__.__dict__.items():
            if isinstance(field, fields.Field):
                setattr(self, field_name, kwargs.get(field_name))

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        """
        Returns a detailed representation of the object.
        """
        return f"<{self.__str__()} object at {hex(id(self))}>"

    def is_namefield_autoincrement(self):
        """Check if the object has a NameField and if its autoincrement is enabled."""
        # Encontra o campo 'name' na classe
        name_field = next(
            (value for key, value in self.__class__.__dict__.items() if key == "name"),
            None,
        )

        if isinstance(name_field, fields.NameField):
            return name_field.autoincrement_enabled

        return False

    def save(self):
        """
        Saves the record in Zendesk (creates or updates).

        Raises:
            CreateRecordError: If the record could not be created.
            UpdateRecordError: If the record could not be updated.
            UniqueConstraintError: If a unique constraint is violated.
        """
        data = {
            "custom_object_record": {
                "custom_object_fields": self.to_save(),
                "name": (
                    getattr(self, "name") or "Unnamed Object"
                    if not self.is_namefield_autoincrement()
                    else None
                ),
                "external_id": getattr(self, "external_id", None),
            }
        }
        # -> If object not contains a NameField type
        # the name field is Unnamed Object or a name passed

        if not hasattr(self, "id") or not self.id:
            response = self.client.post(
                f"/custom_objects/{self.__class__.__name__.lower()}/records", data
            )
            if (
                response.get("details", {}).get("base", [{}])[0].get("description", "")
                == "Name already exists. Try another one."
            ):
                raise UniqueConstraintError(getattr(self, "name"))
            if response.get("status_code", 201) != 201:
                raise CreateRecordError(
                    message=response.get("details", "Error creating record")
                )
            self.id = response["custom_object_record"]["id"]
            self.name = response["custom_object_record"]["name"]
            return response
        response = self.client.patch(
            f"/custom_objects/{self.__class__.__name__.lower()}/records/{self.id}", data
        )
        if response.get("status_code", 200) != 200:
            raise UpdateRecordError(
                message=response.get("details", "Error updating record")
            )
        return response

    def delete(self):
        """
        Deletes the current object from Zendesk using its ID.

        Raises:
            DeleteRecordError: If the record could not be deleted.
        """
        response = self.client.delete(
            f"/custom_objects/{self.__class__.__name__}/records/{self.id}"
        )
        if response.get("status_code", 204) != 204:
            raise DeleteRecordError(
                message=response.get("description", "Error deleting record")
            )

        return response

    def to_dict(self):
        """
        Converts the current object to a dictionary format, including custom fields and
        default fields required by Zendesk API.

        Returns:
            dict: A dictionary containing the object's fields and values.
        """
        default_fields = {
            "id": getattr(self, "id", None),
            "name": getattr(self, "name", None),
            "created_at": getattr(self, "created_at", None),
            "updated_at": getattr(self, "updated_at", None),
            "created_by_user_id": getattr(self, "created_by_user_id", None),
            "updated_by_user_id": getattr(self, "updated_by_user_id", None),
            "external_id": getattr(self, "external_id", None),
        }

        custom_fields = {
            field_name: getattr(self, field_name)
            for field_name, field in self.__class__.__dict__.items()
            if isinstance(field, fields.Field)
        }

        default_fields = {
            key: value for key, value in default_fields.items() if value is not None
        }
        return {**custom_fields, **default_fields}

    def to_save(self):
        """
        Converts the current object to a dictionary format for saving in Zendesk,
        including custom fields and default fields required by the API.

        Returns:
            dict: A dictionary containing the object's fields and values.
        """
        default_fields = {
            "id": getattr(self, "id", None),
            "name": getattr(self, "name", None),
            "created_at": getattr(self, "created_at", None),
            "updated_at": getattr(self, "updated_at", None),
            "created_by_user_id": getattr(self, "created_by_user_id", None),
            "updated_by_user_id": getattr(self, "updated_by_user_id", None),
            "external_id": getattr(self, "external_id", None),
        }
        custom_fields = {}

        for field_name, field in self.__class__.__dict__.items():
            if isinstance(field, (fields.DropdownField, fields.MultiselectField)):
                custom_fields[field_name] = None
                if getattr(self, field_name) is not None:
                    custom_fields[field_name] = self.__class__.__dict__[
                        field_name
                    ].get_to_save(self, None)

            elif isinstance(field, fields.Field):
                custom_fields[field_name] = getattr(self, field_name)

        default_fields = {
            key: value for key, value in default_fields.items() if value is not None
        }
        return {**custom_fields, **default_fields}
