"""Custom fields for custom objects.

This module defines different types of fields that can be used
to represent and manage data within custom objects.
"""

from enum import Enum
import re
from typing import Any, List, Tuple

from unidecode import unidecode

from mercuryorm.exceptions import (
    FieldTypeError,
    InvalidChoiceError,
    InvalidDateFormatError,
    InvalidRegexError,
    RegexCompileError,
)
from mercuryorm.file import FileManagerZendesk, AttachmentFile

DEFAULT_FIELDS = [
    "id",
    "name",
    "created_at",
    "updated_at",
    "created_by_user_id",
    "updated_by_user_id",
    "external_id",
]


class FieldTypes(Enum):
    """
    Enumeration of the different field types available.

    Attributes:
        NAME: A field representing the name of a custom object.
        TEXT: A field representing text data.
        TEXTAREA: A field representing longer text data.
        CHECKBOX: A field representing a boolean value.
        DATE: A field representing a date.
        INTEGER: A field representing an integer.
        DECIMAL: A field representing a decimal value.
        REGEXP: A field validated by a regular expression pattern.
        DROPDOWN: A field representing a dropdown with selectable options.
        LOOKUP: A field representing a relationship to another object.
        MULTISELECT: A field representing multiple selectable options.
    """

    NAME = "name"
    TEXT = "text"
    TEXTAREA = "textarea"
    CHECKBOX = "checkbox"
    DATE = "date"
    INTEGER = "integer"
    DECIMAL = "decimal"
    REGEXP = "regexp"
    DROPDOWN = "dropdown"
    LOOKUP = "lookup"
    MULTISELECT = "multiselect"


class Field:  # pylint: disable=too-few-public-methods
    """
    Base class for all fields.

    Attributes:
        name (str): The name of the field.
        field_type (FieldTypes): The data type of the field.
        data_type (type): The Python type of the field.
    """

    def __init__(
        self,
        name: str,
        field_type: FieldTypes,
        data_type: type,
    ):
        """
        Initialize a Field instance.

        Args:
            name: The name of the field.
            field_type: The data type of the field.
            type: The Python type of the field.
        """
        self.name = name
        self.field_type = field_type
        self.data_type = data_type

    def contribute_to_class(self, cls, name):
        """
        Method to add custom attributes to a class.
        """

    def validate(self, value: Any) -> bool:
        """
        Validate the value of the field.

        Args:
            value: The value to validate.

        Returns:
            True if the value is valid, False otherwise.

        Note:
            This method should be overridden in subclasses to provide custom validation logic.
        """
        if value is None:
            return True
        return isinstance(value, self.data_type)

    def __get__(self, instance: object, owner: type) -> Any:
        """
        Get the value of the field.

        Args:
            instance: The instance of the class.
            owner: The class owning the instance.

        Returns:
            The value of the field.
        """
        return instance.__dict__.get(self.name)

    def __set__(self, instance: object, value: Any) -> None:
        """
        Set the value of the field.

        Args:
            instance: The instance of the class.
            value: The value to set for the field.

        Raises:
            FieldTypeError: If validation fails.
        """
        if not self.validate(value):
            raise FieldTypeError(self.name, self.data_type)
        instance.__dict__[self.name] = value


class NameField(Field):  # pylint: disable=too-few-public-methods
    """
    A field representing the name of a custom object.

    Inherits from Field and uses string as its data type.
    """

    def __init__(
        self,
        unique: bool = False,
        autoincrement_enabled: bool = False,
        autoincrement_prefix: str = "",
        autoincrement_padding: int = 0,
        autoincrement_next_sequence: int = 1,
    ):  # pylint: disable=too-many-arguments
        """
        Initialize a NameField instance.

        Args:
            unique: Indicates whether the field should have unique values.
            autoincrement_enabled: Specifies if the autoincrement feature is enabled.
            autoincrement_prefix: The prefix for the autoincrement feature.
            autoincrement_padding: A positive integer (0-9) specifying the number
                of digits in the autogenerated numbers.
            autoincrement_next_sequence: A positive integer indicating the
                difference between the next sequence number and the current one.
        """
        super().__init__("name", FieldTypes.NAME, str)
        self.unique = unique
        self.autoincrement_enabled = autoincrement_enabled
        self.autoincrement_prefix = autoincrement_prefix
        self.autoincrement_padding = autoincrement_padding
        self.autoincrement_next_sequence = autoincrement_next_sequence

    def __set__(self, instance: object, value: str | None) -> None:
        super().__set__(instance, value)

    def __get__(self, instance: object, owner: type) -> str | None:
        value = super().__get__(instance, owner)
        return value


class TextField(Field):  # pylint: disable=too-few-public-methods
    """
    A field representing text data.

    Inherits from Field and uses string as its data type.
    """

    def __init__(self, name: str):
        """
        Initialize a TextField instance.

        Args:
            name: The name of the text field.
        """
        super().__init__(name, FieldTypes.TEXT, str)

    def __set__(self, instance: object, value: str | None) -> None:
        super().__set__(instance, value)

    def __get__(self, instance: object, owner: type) -> str | None:
        value = super().__get__(instance, owner)
        return value


class TextareaField(Field):  # pylint: disable=too-few-public-methods
    """
    A field representing longer text data.

    Inherits from Field and uses string as its data type.
    """

    def __init__(self, name: str):
        """
        Initialize a TextareaField instance.

        Args:
            name: The name of the textarea field.
        """
        super().__init__(name, FieldTypes.TEXTAREA, str)

    def __set__(self, instance: object, value: str | None) -> None:
        super().__set__(instance, value)

    def __get__(self, instance: object, owner: type) -> str | None:
        value = super().__get__(instance, owner)
        return value


class CheckboxField(Field):  # pylint: disable=too-few-public-methods
    """
    A field representing a boolean value.

    Inherits from Field and uses boolean as its data type.
    """

    def __init__(self, name: str):
        """
        Initialize a CheckboxField instance.

        Args:
            name: The name of the checkbox field.
        """
        super().__init__(name, FieldTypes.CHECKBOX, bool)

    def __set__(self, instance: object, value: bool | None) -> None:
        super().__set__(instance, value)

    def __get__(self, instance: object, owner: type) -> bool | None:
        value = super().__get__(instance, owner)
        return value


class DateField(Field):  # pylint: disable=too-few-public-methods
    """
    A field representing a date.

    Inherits from Field and uses a string representation of a date.
    """

    def __init__(self, name: str):
        """
        Initialize a DateField instance.

        Args:
            name: The name of the date field.
        """
        super().__init__(name, FieldTypes.DATE, str)

    def validate(self, value: str) -> bool:
        """
        Validate the value of the date field.

        Args:
            value: The value to validate.

        Returns:
            True if the value is a valid date string, False otherwise.

        Raises:
            FieldTypeError: If the value is not a string.
        """
        if value is None:
            return True
        if not isinstance(value, str):
            raise FieldTypeError(self.name, str)
        if not self._is_valid_date_format(value):
            raise InvalidDateFormatError(self.name)
        return True

    def _is_valid_date_format(self, date_str: str) -> bool:
        pattern = r"^\d{4}-\d{2}-\d{2}$"
        return bool(re.match(pattern, date_str))

    def __set__(self, instance: object, value: str | None) -> None:
        """
        Set the value of the date field.

        Args:
            instance: The instance of the class.
            value: The value to set for the date field.

        Raises:
            InvalidDateFormatError: If the value has an invalid date format.
        """
        if isinstance(value, str):
            value = value.split("T")[0]
        super().__set__(instance, value)

    def __get__(self, instance: object, owner: type) -> str | None:
        value = super().__get__(instance, owner)
        return value


class IntegerField(Field):  # pylint: disable=too-few-public-methods
    """
    A field representing an integer.

    Inherits from Field and uses integer as its data type.
    """

    def __init__(self, name: str):
        """
        Initialize an IntegerField instance.

        Args:
            name: The name of the integer field.
        """
        super().__init__(name, FieldTypes.INTEGER, int)

    def __set__(self, instance: object, value: int | None) -> None:
        super().__set__(instance, value)

    def __get__(self, instance: object, owner: type) -> int | None:
        value = super().__get__(instance, owner)
        return value


class DecimalField(Field):  # pylint: disable=too-few-public-methods
    """
    A field representing a decimal value.

    Inherits from Field and uses float as its data type.
    """

    def __init__(self, name: str):
        """
        Initialize a DecimalField instance.

        Args:
            name: The name of the decimal field.
        """
        super().__init__(name, FieldTypes.DECIMAL, float)

    def __set__(self, instance: object, value: float | int | None) -> None:
        super().__set__(instance, float(value) if value is not None else None)

    def __get__(self, instance: object, owner: type) -> float | int | None:
        value = super().__get__(instance, owner)
        return value


class RegexpField(Field):  # pylint: disable=too-few-public-methods
    """
    A field validated by a regular expression pattern.

    Inherits from Field and uses string as its data type.
    """

    def __init__(self, name: str, pattern: str):
        """
        Initialize a RegexpField instance.

        Args:
            name: The name of the regexp field.
            pattern: The regular expression pattern for validation.
        """
        super().__init__(name, FieldTypes.REGEXP, str)
        if not self._check_pattern(pattern):
            raise RegexCompileError(self.name)
        self.pattern = pattern

    def _check_pattern(self, pattern: str) -> bool:
        return bool(re.compile(pattern))

    def _check_is_valid_value(self, value: str) -> bool:
        return bool(re.match(self.pattern, value))

    def validate(self, value: str) -> bool:
        """
        Validate the value against the regular expression pattern.

        Args:
            value: The value to validate.

        Returns:
            True if the value matches the pattern, False otherwise.

        Raises:
            FieldTypeError: If the value is not a string.
        """
        if value is None:
            return True
        if not isinstance(value, str):
            raise FieldTypeError(self.name, str)
        if not self._check_is_valid_value(value):
            raise InvalidRegexError(self.name, value)
        return True

    def __set__(self, instance: object, value: str | None) -> None:
        super().__set__(instance, value)

    def __get__(self, instance: object, owner: type) -> str | None:
        value = super().__get__(instance, owner)
        return value


class DropdownField(Field):  # pylint: disable=too-few-public-methods
    """
    A field representing a dropdown with selectable options.

    Inherits from Field and allows a set of predefined choices.
    """

    def __init__(self, name: str, choices: List[str] | List[Tuple[str, str]]):
        """
        Initialize a DropdownField instance.

        Args:
            name: The name of the dropdown field.
            choices: A list of options (str) or key-label tuples (str, str).
        """
        super().__init__(name, FieldTypes.DROPDOWN, str)
        self.choices = choices
        self.to_representation = None
        self.possible_keys = None
        if choices and isinstance(choices[0], tuple):
            self.to_representation = dict(choices)
            self.possible_keys = [key for key, _ in choices]
        else:
            self.possible_keys = [
                unidecode(choice).lower().replace(" ", "_") for choice in choices
            ]

    def __set__(self, instance: object, value: str | None) -> None:
        super().__set__(instance, value)

    def validate(self, value: str) -> bool:
        """
        Validate the value against the allowed choices.

        Args:
            value: The value to validate.

        Returns:
            True if the value is a valid choice.

        Raises:
            InvalidChoiceError: If the value is not in the allowed choices.
        """
        if value is None:
            return True
        if not isinstance(value, str):
            raise FieldTypeError(self.name, str)
        if self.possible_keys and value not in self.possible_keys:
            raise InvalidChoiceError(self.name, value)
        return True

    def get_to_representation(self, instance: object, owner: type) -> str | None:
        """Returns the selected value for representation."""
        value: str = super().__get__(instance, owner)
        if value is None:
            return None
        if self.to_representation:
            return {"value": value, "label": self.to_representation[value]}
        return {"value": value, "label": value}

    def __get__(self, instance: object, owner: type) -> str | None:
        return super().__get__(instance, owner)


class LookupField(Field):  # pylint: disable=too-few-public-methods
    """
    A field representing a relationship to another object.

    Inherits from Field and uses the related object's type for validation.
    """

    def __init__(
        self, name: str, related_object: object, is_custom_object: bool = True
    ):
        """
        Initialize a LookupField instance.

        Args:
            name: The name of the lookup field.
            related_object: The class of the related object.
            is_custom_object: Whether the related object is a custom object.
        """
        super().__init__(name, FieldTypes.LOOKUP, type(related_object))
        self.related_object = related_object
        self.is_custom_object = is_custom_object

    def to_dict(self, value: object) -> dict:
        """
        Convert the lookup field to a dictionary format.

        Args:
            value: The related object to be linked.

        Returns:
            A dictionary with the field name and the object's ID.

        Raises:
            ValueError: If the related object lacks an 'id' attribute.
        """
        if not hasattr(value, "id"):
            raise ValueError("The related object does not have an ID.")
        return {self.name: value.id}

    def to_zendesk(self) -> dict:
        """
        Convert the lookup field to the Zendesk API format.

        Returns:
            The Zendesk-compatible field configuration.
        """
        if isinstance(self.related_object, str):
            target_type = f"zen:custom_object:{self.related_object}"
        else:
            target_type = (
                f"zen:custom_object:{self.related_object.__class__.__name__.lower()}"
            )
        return {
            "type": "lookup",
            "relationship_target_type": target_type,
            "key": self.name,
            "title": self.name.capitalize(),
        }

    def __set__(self, instance: object, value: object | None) -> None:
        super().__set__(instance, value)

    def __get__(self, instance: object, owner: type) -> object | None:
        value = super().__get__(instance, owner)
        return value


class MultiselectField(Field):  # pylint: disable=too-few-public-methods
    """
    A field representing multiple selectable options.

    Inherits from Field and uses a list of selected values.
    """

    def __init__(self, name: str, choices: List[str] | List[Tuple[str, str]]):
        """
        Initialize a MultiselectField instance.

        Args:
            name: The name of the multiselect field.
            choices: A list of options (str) or key-label tuples (str, str).
        """
        super().__init__(name, FieldTypes.MULTISELECT, list)
        self.choices = choices
        self.to_representation = None
        self.possible_keys = None
        if choices and isinstance(choices[0], tuple):
            self.to_representation = dict(choices)
            self.possible_keys = [key for key, _ in choices]
        else:
            self.possible_keys = [
                unidecode(choice).lower().replace(" ", "_") for choice in choices
            ]

    def validate(self, value: str) -> bool:
        """
        Validate the selected values against allowed choices.

        Args:
            value: The value to validate.

        Returns:
            True if all selected values are valid choices.

        Raises:
            InvalidChoiceError: If any selected value is invalid.
        """
        if value is None:
            return True
        if not isinstance(value, list):
            raise FieldTypeError(self.name, list)
        for item in value:
            if self.possible_keys and item not in self.possible_keys:
                raise InvalidChoiceError(self.name, item)
        return True

    def get_to_representation(self, instance: object, owner: type) -> list[str] | None:
        """Returns the list of selected values for representation."""
        value: list[str] = super().__get__(instance, owner)
        if value is None:
            return None
        if self.to_representation:
            return [
                {"value": item, "label": self.to_representation[item]} for item in value
            ]
        return [{"value": item, "label": item} for item in value]

    def __get__(self, instance: object, owner: type) -> List[str] | None:
        return super().__get__(instance, owner)

    def __set__(self, instance: object, value: List[str] | None) -> None:
        super().__set__(instance, value)


class AttachmentField(Field):  # pylint: disable=too-many-instance-attributes
    """
    A field representing an attachment file.
    """

    def __init__(
        self, field_name, *, ticket_field_name, file_manager=FileManagerZendesk
    ):  # pylint: disable=super-init-not-called
        """
        Initialize an AttachmentField instance.
        """
        self.field_name = field_name
        self.field_type = FieldTypes.TEXT
        self.data_type = AttachmentFile
        self.ticket_field_name = ticket_field_name
        self._file_manager = file_manager

    def get_to_representation(self, instance: object, owner: type) -> dict | None:
        """Returns the selected value for representation."""
        value: AttachmentFile = super().__get__(instance, owner)
        if value is None:
            return None
        return {
            "id": str(value.id),
            "filename": value.filename,
            "url": value.url,
            "size": value.size,
        }

    def contribute_to_class(self, cls, name):
        self.model_file_attribute_name = f"__{name}_file"  # pylint: disable=attribute-defined-outside-init
        self.id_field_name = f"{name}_id"  # pylint: disable=attribute-defined-outside-init
        self.url_field_name = f"{name}_url"  # pylint: disable=attribute-defined-outside-init
        self.filename_field_name = f"{name}_filename"  # pylint: disable=attribute-defined-outside-init
        self.size_field_name = f"{name}_size"  # pylint: disable=attribute-defined-outside-init

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if not hasattr(instance, self.model_file_attribute_name):
            attach_id = getattr(instance, self.id_field_name, None)
            attach_url = getattr(instance, self.url_field_name, None)
            attach_filename = getattr(instance, self.filename_field_name, None)
            attach_size = getattr(instance, self.size_field_name, None)

            if not attach_id:
                return None

            setattr(
                instance,
                self.model_file_attribute_name,
                AttachmentFile(
                    attachment_id=attach_id,
                    attachment_url=attach_url,
                    attachment_size=attach_size,
                    attachment_filename=attach_filename,
                ),
            )
        return getattr(instance, self.model_file_attribute_name)

    def __set__(self, instance, value):
        if value is not None:
            if isinstance(value, AttachmentFile):
                setattr(instance, self.model_file_attribute_name, value)
                setattr(instance, self.id_field_name, value.id)
                setattr(instance, self.url_field_name, value.url)
                setattr(instance, self.filename_field_name, value.filename)
                setattr(instance, self.size_field_name, value.size)
            else:
                raise ValueError(
                    "AttachmentField only accepts AttachmentFile instances."
                )
