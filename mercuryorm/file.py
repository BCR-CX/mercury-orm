"""
Manage file attachments.
"""

import uuid
from typing import Optional

from mercuryorm.client.connection import ZendeskAPIClient


class FileManagerZendesk:
    """
    Zendesk file manager class.
    """

    ENDPOINT_ATTACHMENT = "/attachments/{attachment_id}.json"
    ENDPOINT_TICKET = "/tickets/{ticket_id}.json"

    def __init__(self) -> None:
        """
        Initializes the FileManagerZendesk class.

        Sets the client instance that will be used for all operations.
        """
        self._client = ZendeskAPIClient()

    def upload(self, filename: str, content: bytes) -> dict:
        """
        Upload a file to Zendesk.
        """
        return self._client.upload_file(filename, content)

    def send_to_ticket(
        self, ticket_id: int, token: str, comment: str = "Anexo adicionado."
    ):
        """
        Sends the uploaded attachment to the given ticket.
        """
        data = {"ticket": {"comment": {"body": comment, "uploads": [token]}}}
        return self._client.put(
            self.ENDPOINT_TICKET.format(ticket_id=ticket_id), data=data
        )

    def get_attachment_details(self, attachment_id: str) -> dict:
        """
        Gets the details of a specific attachment.
        """
        return self._client.get(
            self.ENDPOINT_ATTACHMENT.format(attachment_id=attachment_id)
        )


class AttachmentFile:
    """
    Class representing an attachment file.
    """

    def __init__(
        self,
        *,
        filename: Optional[str] = None,
        attachment_id: Optional[str] = None,
        content: Optional[bytes] = None,
        save_fast: Optional[bool] = False,
        file_manager: FileManagerZendesk = FileManagerZendesk
    ):
        """
        Initialize an AttachmentFile instance.
        """

        self._id = attachment_id
        self.saved = False
        self._content = content
        self.file_manager = file_manager
        self.zendesk_data = None

        self._filename = filename or str(uuid.uuid4())

        if content and save_fast:
            self.save()

    def __bool__(self) -> bool:
        return bool(self.id or self.content)

    def __str__(self) -> str:
        """
        String representation of the AttachmentFile instance.
        """
        return str(self.id)

    @property
    def content(self) -> bytes:
        """
        Content of the file.
        """
        return self._content

    @content.setter
    def content(self, value: bytes) -> None:
        """
        Set the content of the file.
        """
        if not isinstance(value, bytes):
            raise ValueError("Content attribute must be of type bytes.")
        self._content = value
        self.saved = False

    @property
    def id(self) -> str:  # pylint: disable=invalid-name
        """
        Attachment ID.
        """
        if not self.zendesk_data:
            return self._id
        return self.zendesk_data["id"]

    @property
    def filename(self) -> str | None:
        """
        Attachment filename.
        """
        return self._get_zendesk_data_value("file_name")

    @property
    def url(self) -> str | None:
        """
        Attachment URL.
        """
        return self._get_zendesk_data_value("content_url")

    @property
    def size(self) -> int | None:
        """
        Attachment size in KB.
        """
        return self._get_zendesk_data_value("size")

    def _get_zendesk_data_value(self, key: str) -> int | str | None:
        """
        Get a value from the zendesk_data dictionary.
        """
        if not self._id:
            return None
        if not self.zendesk_data:
            self.zendesk_data = self._get_attachment_details(self._id)
            self.saved = True
        if self.saved and self.zendesk_data:
            return self.zendesk_data[key]
        raise ValueError("File not saved yet, to save use save() method.")

    def _upload_attachment(self, filename: str, content: bytes) -> dict:
        """
        Sends the file to Zendesk.
        """
        response = self.file_manager().upload(filename, content)
        return response["upload"]

    def _send_attachment_to_ticket(
        self, ticket_id: str, token: str, comment: str
    ) -> dict:
        """
        Sends the uploaded attachment to the given ticket.
        """
        response = self.file_manager().send_to_ticket(ticket_id, token, comment)
        return response

    def _get_attachment_details(self, attachment_id: str) -> dict:
        """
        Gets the details of a specific attachment.
        """
        response = self.file_manager().get_attachment_details(attachment_id)
        return response["attachment"]

    def save(self) -> None:
        """
        Save the file to Zendesk.
        """
        if not self.saved:
            if not isinstance(self.content, bytes):
                raise ValueError("Content attribute must be of type bytes.")
            upload_data = self._upload_attachment(self._filename, self.content)
            self.zendesk_data = upload_data["attachment"]
            self.token = upload_data["token"]
            self.saved = True

    def save_with_ticket(self, ticket_id: int, comment: str) -> dict:
        """
        Save the file to Zendesk and send it to the given ticket.
        """
        if not self.saved:
            self.save()
        return self._send_attachment_to_ticket(ticket_id, self.token, comment)
