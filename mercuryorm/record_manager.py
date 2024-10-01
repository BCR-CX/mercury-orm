"""
This module handles the management of custom object records for integration
with the Zendesk API, including creating, retrieving, and deleting records.
"""

import requests
from mercuryorm.managers import QuerySet
from mercuryorm.zendesk_manager import ZendeskAPIClient
from mercuryorm.exceptions import BadRequestError, NotFoundError


class RecordManager:
    """
    Manages custom object records by interacting with the Zendesk API.
    Provides methods to create, retrieve, filter, and delete records.
    """

    def __init__(self, model):
        self.model = model
        self.queryset = QuerySet(model)
        self.client = ZendeskAPIClient()

    def create(self, **kwargs):
        """
        Creates a new record for the Custom Object.
        """
        record = self.model(**kwargs)
        return record.save()

    def get(self, **kwargs):
        """
        Returns a single record based on the given parameters.
        If 'id' is given, searches directly by URL.
        Otherwise, uses the filter method for other criteria.
        """
        if "id" in kwargs:
            record_id = kwargs.pop("id")
            try:
                response = self.client.get(
                    f"/custom_objects/{self.model.__name__.lower()}/records/{record_id}"
                )
            except requests.exceptions.HTTPError as e:  # pylint: disable=invalid-name
                if e.response.status_code == 400:
                    error_response = e.response.json()
                    raise BadRequestError(
                        f"Bad request for record with ID {record_id}. Response: {error_response}"
                    ) from e
                if e.response.status_code == 404:
                    raise NotFoundError(self.model.__name__, record_id) from e
                raise e
            record_data = response.get("custom_object_record", {})
            record = self.queryset.parse_record_fields(record_data)
            return record

        result = self.filter(**kwargs)
        if len(result) == 0:
            raise ValueError(f"{self.model.__name__} matching query does not exist.")
        if len(result) > 1:
            raise ValueError(
                f"Multiple {self.model.__name__} objects returned; expected exactly one."
            )
        return result[0]

    def all(self):
        """
        Returns all records using QuerySet.
        """
        return self.queryset.all()

    def filter(self, **criteria):
        """
        Filters records based on the given criteria using QuerySet.
        """
        return self.queryset.filter(**criteria)

    def delete(self, record_id):
        """
        Deletes a record by ID.
        """
        return self.client.delete(
            f"/custom_objects/{self.model.__name__.lower()}/records/{record_id}"
        )

    def last(self):
        """
        Returns the last record based on the update date (updated_at).
        Sorts the records by 'updated_at' in descending order and returns the first one.
        """
        params = {"sort": "-updated_at", "page[size]": 1}

        response = self.client.get(
            f"/custom_objects/{self.model.__name__.lower()}/records", params=params
        )

        if response.get("custom_object_records"):
            record = self.queryset.parse_record_fields(
                response["custom_object_records"][0]
            )
            return record
        return None
