"""
This module contains the `ZendeskObjectManager` class, which manages the operations
related to Zendesk custom objects and their fields.
"""

import os
import logging
from unidecode import unidecode
from dotenv import load_dotenv  # pylint: disable=import-error
from mercuryorm.client.connection import ZendeskAPIClient
from mercuryorm import fields


load_dotenv()


class ZendeskObjectManager:
    """
    Manages the interactions with Zendesk custom objects, including creating objects,
    fields, and records. Also provides methods to list existing objects and fields.
    """

    def __init__(self, email=os.getenv("ZENDESK_EMAIL", "mock@mock.com")):
        """
        Initializes the ZendeskObjectManager with the given email for authentication.
        Args:
            email (str): The email associated with the Zendesk account.
        """
        self.client = ZendeskAPIClient(email)

    def get_custom_object(self, key):
        """
        Returns the Custom Object with the given key, if it exists.
        Args:
            key (str): The key of the custom object.

        Returns:
            dict: The custom object details if found, otherwise None.
        """
        custom_objects = self.list_custom_objects()
        for obj in custom_objects:
            if obj["key"] == key:
                return obj
        return None

    def create_custom_object(self, key, title, description=""):
        """
        Creates a Custom Object (equivalent to a table in relational databases).
        Args:
            key (str): The key for the custom object.
            title (str): The title for the custom object.
            description (str, optional): A description for the custom object.

        Returns:
            dict: The response from Zendesk API with the newly created custom object.
        """
        endpoint = "/custom_objects"
        data = {
            "custom_object": {
                "key": key,
                "title": title,
                "title_pluralized": f"{title}s",
                "description": description,
                "include_in_list_view": True,
            }
        }
        return self.client.post(endpoint, data)

    def get_or_create_custom_object(self, key, title, description):
        """
        Checks if the Custom Object already exists, and creates it if it doesn't.
        Args:
            key (str): The key for the custom object.
            title (str): The title for the custom object.
            description (str): A description for the custom object.

        Returns:
            tuple: A tuple of the custom object and a boolean indicating if it was created.
        """
        existing_object = self.get_custom_object(key)
        if existing_object:
            return existing_object, False

        new_object = self.create_custom_object(key, title, description)
        return new_object, True

    def list_custom_object_fields(self, custom_object_key):
        """
        Returns a list of existing fields from a Custom Object.
        Args:
            custom_object_key (str): The key of the custom object to list fields for.

        Returns:
            list: A list of field keys for the custom object.
        """
        endpoint = f"/custom_objects/{custom_object_key}/fields"
        response = self.client.get(endpoint)
        return [field["key"] for field in response.get("custom_object_fields", [])]

    def create_custom_object_field(
        self, custom_object_key, field_type, key, title, **kwargs
    ):
        """
        Creates fields (columns) for a Custom Object.
        Args:
            custom_object_key (str): The key of the custom object to add fields to.
            field_type (str): The type of the field (e.g., text, integer).
            key (str): The key of the field.
            title (str): The title of the field.
            choices (list, optional): A list of choices if the field is a dropdown or multiselect.

        Returns:
            dict: The response from Zendesk API with the newly created field.
        """
        choices = kwargs.get("choices")
        if key == "name":
            return {"message": "Field 'name' is not allowed to be created"}
        if key == "external_id":
            return {"message": "Field 'external_id' is not allowed to be created"}
        valid_field_types = [
            "text",
            "textarea",
            "checkbox",
            "date",
            "integer",
            "decimal",
            "regexp",
            "dropdown",
            "lookup",
            "multiselect",
        ]
        if field_type not in valid_field_types:
            raise ValueError(
                f"Invalid field type '{field_type}'. Must be one of {valid_field_types}."
            )
        endpoint = f"/custom_objects/{custom_object_key}/fields"
        data = {
            "custom_object_field": {
                "type": field_type,  # Field type: "text", "integer", etc.
                "key": key,
                "title": title,
            }
        }
        if field_type in ["dropdown", "multiselect"] and choices:
            data["custom_object_field"]["custom_field_options"] = [
                {
                    "name": choice,
                    "raw_name": choice,
                    "value": unidecode(choice).lower().replace(" ", "_"),
                }
                for choice in choices
            ]
        if field_type == "lookup":
            data["custom_object_field"][
                "relationship_target_type"
            ] = f"zen:custom_object:{key}"

        return self.client.post(endpoint, data)

    def create_custom_object_record(self, custom_object_key, record_data):
        """
        Adds a record (row) to a Custom Object.
        Args:
            custom_object_key (str): The key of the custom object.
            record_data (dict): The data for the new record.

        Returns:
            dict: The response from Zendesk API with the newly created record.
        """
        endpoint = f"/custom_objects/{custom_object_key}/records"
        data = {"record": record_data}
        return self.client.post(endpoint, data)

    def list_custom_objects(self):
        """
        Lists all custom objects.
        Returns:
            list: A list of custom objects.
        """
        endpoint = "/custom_objects"
        return self.client.get(endpoint).get("custom_objects", [])

    def create_custom_object_from_model(self, model):
        """
        Creates a Custom Object and its fields based on the provided template/model.
        Args:
            model (type): The model class representing the custom object.

        Returns:
            None
        """
        custom_object_key = model.__name__.lower()
        self.create_custom_object(
            key=custom_object_key,
            title=model.__name__,
            description=f"Custom Object for {model.__name__}",
        )

        existing_fields = self.list_custom_object_fields(custom_object_key)

        for field_name, field in model.__dict__.items():
            if isinstance(field, fields.Field):
                field_key = field.name.lower()
                if field_key not in existing_fields and field_key != "name":
                    field_type = field.__class__.__name__.lower()
                    if field_type.endswith("field"):
                        field_type = field_type.replace("field", "")
                    choices = getattr(field, "choices", None)
                    self.create_custom_object_field(
                        custom_object_key=custom_object_key,
                        field_type=field_type,
                        key=field_key,
                        title=field_name.capitalize(),
                        choices=choices,
                    )
                    logging.info(
                        "Field '%s' created for Custom Object '%s'.",
                        field_key,
                        custom_object_key,
                    )

    def get_or_create_custom_object_from_model(self, model):
        """
        Checks if the Custom Object already exists and creates missing fields.
        Args:
            model (type): The model class representing the custom object.

        Returns:
            tuple: A tuple of the custom object and a boolean indicating if it was created.
        """
        custom_object_key = model.__name__.lower()

        custom_object, created = self.get_or_create_custom_object(
            key=custom_object_key,
            title=model.__name__,
            description=f"Custom Object for {model.__name__}",
        )

        existing_fields = self.list_custom_object_fields(custom_object_key)

        for field_name, field in model.__dict__.items():
            if isinstance(field, fields.Field):
                field_key = field.name.lower()
                if field_key not in existing_fields and field_key != "name":
                    field_type = field.__class__.__name__.lower()
                    if field_type.endswith("field"):
                        field_type = field_type.replace("field", "")
                    choices = getattr(field, "choices", None)
                    self.create_custom_object_field(
                        custom_object_key=custom_object_key,
                        field_type=field_type,
                        key=field_key,
                        title=field_name.capitalize(),
                        choices=choices,
                    )
                    logging.info(
                        "Field '%s' created for Custom Object '%s'.",
                        field_key,
                        custom_object_key,
                    )

        return custom_object, created
