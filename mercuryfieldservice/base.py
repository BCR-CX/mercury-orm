"""
Module for handling CustomObject base functionality, including saving, deleting,
and managing fields for integration with Zendesk API.
"""

from mercuryfieldservice.client.connection import ZendeskAPIClient
from mercuryfieldservice import fields
from mercuryfieldservice.record_manager import RecordManager


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
        self.id = None  # pylint: disable=invalid-name
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

    def save(self):
        """
        Saves the record in Zendesk (creates or updates).
        """
        data = {
            "custom_object_record": {
                "custom_object_fields": self.to_dict(),
                "name": getattr(self, "name", "Unnamed Object"),
            }
        }

        if not hasattr(self, "id") or not self.id:
            response = ZendeskAPIClient().post(
                f"/custom_objects/{self.__class__.__name__.lower()}/records", data
            )
            self.id = response["custom_object_record"]["id"]
            return response
        return ZendeskAPIClient().patch(
            f"/custom_objects/{self.__class__.__name__.lower()}/records/{self.id}", data
        )

    def delete(self):
        """
        Deletes the current object from Zendesk using its ID.
        """
        return ZendeskAPIClient().delete(
            f"/custom_objects/{self.__class__.__name__}/records/{self.id}"
        )

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
            "codigo": getattr(self, "codigo", None),
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
