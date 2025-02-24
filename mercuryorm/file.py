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


class AttachmentFile:  # pylint: disable=too-many-instance-attributes
    """
    Class representing an attachment file.
    """

    def __init__(
        self,
        *,
        attachment_id: Optional[str] = None,
        attachment_url: Optional[str] = None,
        attachment_size: Optional[int] = None,
        attachment_filename: Optional[str] = None,
        content: Optional[bytes] = None,
        save_fast: Optional[bool] = False,
        file_manager: FileManagerZendesk = FileManagerZendesk,
    ):
        """
        Initialize an AttachmentFile instance.
        """
        self._attachment_id = attachment_id
        self._attachment_url = attachment_url
        self._attachment_size = attachment_size
        self._attachment_filename = attachment_filename or str(uuid.uuid4())
        self._content = content
        self.file_manager = file_manager
        self.zendesk_data = None
        self.saved = False

        if attachment_id:
            self.saved = True

        if content:
            self.saved = False
            if save_fast:
                self.save()

    def __bool__(self) -> bool:
        return bool(self.id or self.content)

    def __str__(self) -> str:
        """
        String representation of the AttachmentFile instance.
        """
        return f"AttachmentFile(id={self.id}, filename={self.filename}, saved={self.saved})"

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
        return self._attachment_id

    @property
    def filename(self) -> str | None:
        """
        Attachment filename.
        """
        return self._attachment_filename

    @property
    def url(self) -> str | None:
        """
        Attachment URL.
        """
        return self._attachment_url

    @property
    def size(self) -> int | None:
        """
        Attachment size in KB.
        """
        return self._attachment_size

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

    def save(self) -> None:
        """
        Save the file to Zendesk.
        """
        if not self.saved:
            if not isinstance(self.content, bytes):
                raise ValueError("Content attribute must be of type bytes.")
            upload_data = self._upload_attachment(self.filename, self.content)
            self._attachment_id = upload_data["attachment"]["id"]
            self._attachment_filename = upload_data["attachment"]["file_name"]
            self._attachment_url = upload_data["attachment"]["content_url"]
            self._attachment_size = upload_data["attachment"]["size"]
            self.token = upload_data["token"]
            self.saved = True

    def save_with_ticket(self, ticket_id: int, comment: str) -> dict:
        """
        Save the file to Zendesk and send it to the given ticket.
        """
        if not self.saved:
            self.save()
        return self._send_attachment_to_ticket(ticket_id, self.token, comment)
