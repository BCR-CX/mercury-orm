"""
For Manager and querysets to Records CustomObject
"""

from mercuryorm.client.connection import ZendeskAPIClient


class QuerySet:
    """
    For Manager and querysets to Records CustomObject.
    """

    def __init__(self, model):
        self.model = model
        self.base_url = f"/custom_objects/{self.model.__name__.lower()}/records"
        self.client = ZendeskAPIClient()

    def all(self):
        """
        Returns all records from the Custom Object without metadata or links.
        """
        response = self.client.get(self.base_url)
        records = self._parse_response(response)
        return records

    def all_with_pagination(self, page_size=100, after_cursor=None, before_cursor=None):
        """
        Returns all records that support pagination, including metadata and links.
        """
        params = {"page[size]": page_size}
        if after_cursor:
            params["page[after]"] = after_cursor
        if before_cursor:
            params["page[before]"] = before_cursor

        response = self.client.get(self.base_url, params=params)
        return (
            self._parse_response(response),
            response.get("meta", {}),
            response.get("links", {}),
        )

    def filter(self, **kwargs):
        """
        Filters records in memory based on the parameters provided.
        The Zendesk API does not support native filtering by custom fields, so
        we take all records and filter them locally.
        """
        records = self.all()

        filtered_records = []
        for record in records:
            match = True
            for key, value in kwargs.items():
                if getattr(record, key, None) != value:
                    match = False
                    break
            if match:
                filtered_records.append(record)

        return filtered_records

    def _parse_response(self, response):
        """
        Internal method to process the API response and extract the records.
        """
        records = []
        for record_data in response.get("custom_object_records", []):
            record = self.parse_record_fields(record_data)
            records.append(record)
        return records

    def parse_record_fields(self, record_data):
        """
        Internal method to process the API response and extract the records fields.
        """
        fields = record_data.get("custom_object_fields", {})
        record = self.model(**fields)
        # Default Fields Zendesk
        record.id = record_data.get("id")
        record.name = record_data.get("name")
        record.created_at = record_data.get("created_at")
        record.updated_at = record_data.get("updated_at")
        record.created_by_user_id = record_data.get("created_by_user_id")
        record.updated_by_user_id = record_data.get("updated_by_user_id")
        record.external_id = record_data.get("external_id")
        return record
