"""
Module for manager Exceptions
"""


class ZendeskAPIError(Exception):
    """Base exception for all Zendesk API related errors."""


class BadRequestError(ZendeskAPIError):
    """Exception for when the API request returns a 400 error."""

    def __init__(
        self, message="Bad request. The data provided is invalid or malformed."
    ):
        self.message = message
        super().__init__(self.message)


class NotFoundError(ZendeskAPIError):
    """Exception for when a resource is not found (404 error)."""

    def __init__(self, resource_name, resource_id):
        self.message = f"{resource_name} with id '{resource_id}' not found."
        super().__init__(self.message)


class MultipleObjectsReturnedError(ZendeskAPIError):
    """Exception for when more than one object is returned when using the 'get()' method."""

    def __init__(self, model_name):
        self.message = f"Multiple {model_name} objects returned; expected exactly one."
        super().__init__(self.message)


class ZendeskUnauthorizedError(ZendeskAPIError):
    """Exception for authentication errors (error 401)."""

    def __init__(
        self,
        message="Unauthorized request. Please check your API token or credentials.",
    ):
        self.message = message
        super().__init__(self.message)


class ZendeskForbiddenError(ZendeskAPIError):
    """Exception for permission errors (error 403)."""

    def __init__(
        self,
        message="Access forbidden. You don't have permission to access this resource.",
    ):
        self.message = message
        super().__init__(self.message)


class FieldsError(Exception):
    """Base exception for all field errors."""


class UniqueConstraintError(FieldsError):
    """Exception for when a field with a unique constraint is violated."""

    def __init__(self, field_name):
        self.message = f"Field '{field_name}' must be unique, but a record with this value already exists."  # pylint: disable=line-too-long
        super().__init__(self.message)


class NameFieldUniqueAndAutoIncrementConflictError(FieldsError):
    """Exception for when a NameField is both unique and autoincremented"""

    def __init__(self):
        self.message = "Field must be either unique or autoincremented, not both."
        super().__init__(self.message)


class NameFieldError(FieldsError):
    "Exception for when a NameField is not named 'name' or when there is more than one NameField."

    def __init__(self):
        self.message = "Only one NameField is allowed per custom object, and its name must be 'name'."  # pylint: disable=line-too-long
        super().__init__(self.message)
