"""
For Manager and querysets to Records CustomObject
"""

from urllib.parse import parse_qs, urlparse
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
        Returns the 100 first records from the Custom Object without metadata or links.
        """
        response = self.client.get(self.base_url)
        records = self._parse_response(response)
        return records

    def all_of(self):
        """
        Returns all records from the Custom Object, handling pagination automatically.
        """
        records = []
        next_cursor = None

        while True:
            params = {"page[size]": 100}
            if next_cursor:
                params["page[after]"] = next_cursor

            response = self.client.get(self.base_url, params=params)

            if "error" in response:
                raise ValueError(
                    f"Error from Zendesk API: {response['error']} - {response.get('description')}"
                )

            records.extend(self._parse_response(response))

            links = response.get("links", {})
            next_cursor_url = links.get("next")

            if not next_cursor_url:
                break

            parsed_url = urlparse(next_cursor_url)
            next_cursor = parse_qs(parsed_url.query).get("page[after]", [None])[0]
        return records

    def all_with_pagination(self, page_size=100, after_cursor=None, before_cursor=None):
        """
        Returns a paginated response including metadata and links.
        """
        params = {"page[size]": page_size}
        if after_cursor:
            params["page[after]"] = after_cursor
        if before_cursor:
            params["page[before]"] = before_cursor

        response = self.client.get(self.base_url, params=params)

        if "error" in response:
            raise ValueError(
                f"Error from Zendesk API: {response['error']} - {response.get('description')}"
            )

        return {
            "count": self.count(),
            "results": self._parse_response(response),
            "meta": response.get("meta", {}),
            "links": response.get("links", {}),
        }
    def find(self, filters):
        """
        Returns a list of records that match the specified filter.  
        The filter is a dictionary and can take the following forms:  
            - A single dictionary with a key (field_name) and a value
            that is another dictionary containing an operator and a value.  
            - Key(s) named `$and` or `$or`, where the value is a 
            list of dictionaries. Each dictionary contains a key (field_name) and a value
            that is another dictionary with an operator and a value.
        """
        records = []
        next_cursor = None

        while True:
            params = {"page[size]": 100}
            if next_cursor:
                params["page[after]"] = next_cursor

            response = self.client.post(self.base_url+"/search", data={"filter":filters})

            if "error" in response:
                raise ValueError(
                    f"Error from Zendesk API: {response['error']} - {response.get('description')}"
                )

            records.extend(self._parse_response(response))
            links = response.get("links", {})
            next_cursor_url = links.get("next")

            if not next_cursor_url:
                break
            # Extract value from 'page[after]' of URL 'next'
            # Example "next_cursor_url": "/custom_objects/myobject/records?page[after]=xyz"
            parsed_url = urlparse(next_cursor_url)
            next_cursor = parse_qs(parsed_url.query).get("page[after]", [None])[0]
        return records

    def find_with_pagination(self, filters, page_size=100, after_cursor=None, before_cursor=None):
        """
        Returns a paginated response including metadata and links.
        The instrunctions for the filter are the same as the find method.
        """
        params = {"page[size]": page_size}
        if after_cursor:
            params["page[after]"] = after_cursor
        if before_cursor:
            params["page[before]"] = before_cursor

        response = self.client.post(self.base_url+"/search", data={"filter":filters}, params=params)

        if "error" in response:
            raise ValueError(
                f"Error from Zendesk API: {response['error']} - {response.get('description')}"
            )

        return {
            "count": self.count(),
            "results": self._parse_response(response),
            "meta": response.get("meta", {}),
            "links": response.get("links", {}),
        }

    def search_with_pagination(
        self, word, page_size=100, after_cursor=None, before_cursor=None
    ):
        """
        Returns paginated search results with a word.
        """
        params = {"query": word, "sort": "", "page[size]": page_size}
        if after_cursor:
            params["page[after]"] = after_cursor
        if before_cursor:
            params["page[before]"] = before_cursor

        response = self.client.get(
            f"/custom_objects/{self.model.__name__.lower()}/records/search",
            params=params,
        )

        results = []
        if response.get("custom_object_records"):
            records = response.get("custom_object_records", [])
            for record in records:
                results.append(self.parse_record_fields(record))

        return {
            "count": response.get("count", ""),
            "results": results,
            "meta": response.get("meta", {}),
            "links": response.get("links", {}),
        }

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

    def count(self):
        """
        Deletes a record by ID.
        """
        response = self.client.get(
            f"/custom_objects/{self.model.__name__.lower()}/records/count"
        )
        return response["count"]["value"]

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
