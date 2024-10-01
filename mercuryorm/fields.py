""" Custom fields for custom objects.

This module defines different types of fields that can be used
to represent and manage data within custom objects.
"""


class Field:  # pylint: disable=too-few-public-methods
    """
    Base class for all fields.

    Attributes:
        name (str): The name of the field.
        field_type (type): The type of the field (e.g., str, int).
    """

    def __init__(self, name, field_type):
        """
        Initializes a Field object.

        Args:
            name (str): The name of the field.
            field_type (type): The data type of the field (e.g., str, int).
        """
        self.name = name
        self.field_type = field_type


class TextField(Field):  # pylint: disable=too-few-public-methods
    """
    A field representing text data.

    Inherits from Field and uses string as its data type.
    """

    def __init__(self, name):
        """
        Initializes a TextField object.

        Args:
            name (str): The name of the text field.
        """
        super().__init__(name, str)


class TextareaField(Field):  # pylint: disable=too-few-public-methods
    """
    A field representing longer text data.

    Inherits from Field and uses string as its data type.
    """

    def __init__(self, name):
        """
        Initializes a TextareaField object.

        Args:
            name (str): The name of the textarea field.
        """
        super().__init__(name, str)


class CheckboxField(Field):  # pylint: disable=too-few-public-methods
    """
    A field representing a boolean value.

    Inherits from Field and uses boolean as its data type.
    """

    def __init__(self, name):
        """
        Initializes a CheckboxField object.

        Args:
            name (str): The name of the checkbox field.
        """
        super().__init__(name, bool)


class DateField(Field):  # pylint: disable=too-few-public-methods
    """
    A field representing a date.

    Inherits from Field and uses a string representation of a date.
    """

    def __init__(self, name):
        """
        Initializes a DateField object.

        Args:
            name (str): The name of the date field.
        """
        super().__init__(name, "date")


class IntegerField(Field):  # pylint: disable=too-few-public-methods
    """
    A field representing an integer.

    Inherits from Field and uses integer as its data type.
    """

    def __init__(self, name):
        """
        Initializes an IntegerField object.

        Args:
            name (str): The name of the integer field.
        """
        super().__init__(name, int)


class DecimalField(Field):  # pylint: disable=too-few-public-methods
    """
    A field representing a decimal value.

    Inherits from Field and uses float as its data type.
    """

    def __init__(self, name):
        """
        Initializes a DecimalField object.

        Args:
            name (str): The name of the decimal field.
        """
        super().__init__(name, float)


class RegexpField(Field):  # pylint: disable=too-few-public-methods
    """
    A field representing a regular expression.

    Inherits from Field and uses a regular expression pattern.
    """

    def __init__(self, name, pattern):
        """
        Initializes a RegexpField object.

        Args:
            name (str): The name of the regexp field.
            pattern (str): The regular expression pattern for the field.
        """
        super().__init__(name, "regexp")
        self.pattern = pattern


class DropdownField(Field):  # pylint: disable=too-few-public-methods
    """
    A field representing a dropdown with selectable options.

    Inherits from Field and allows a set of predefined choices.
    """

    def __init__(self, name, choices):
        """
        Initializes a DropdownField object.

        Args:
            name (str): The name of the dropdown field.
            choices (list): A list of options to select from.
        """
        super().__init__(name, "dropdown")
        self.choices = choices


class LookupField(Field):  # pylint: disable=too-few-public-methods
    """
    A field representing a relationship to another object.

    Inherits from Field and uses a related custom object.
    """

    def __init__(self, name, related_object):
        """
        Initializes a LookupField object.

        Args:
            name (str): The name of the lookup field.
            related_object (str or object): The related object this field points to.
        """
        super().__init__(name, "lookup")
        self.related_object = related_object

    def to_dict(self, value):
        """
        Converts the lookup field to a dictionary format.

        Args:
            value (object): The related object to be linked.

        Raises:
            ValueError: If the related object does not have an ID.

        Returns:
            dict: The dictionary representation of the lookup field.
        """
        if not hasattr(value, "id"):
            raise ValueError("The related object does not have an ID.")
        return {self.name: value.id}

    def to_zendesk(self):
        """
        Converts the lookup field to the Zendesk API format.

        Returns:
            dict: The JSON representation for Zendesk API.
        """
        if isinstance(self.related_object, str):
            target_type = f"zen:custom_object:{self.related_object}"
        else:
            target_type = f"zen:custom_object:{self.related_object.__name__.lower()}"

        return {
            "type": "lookup",
            "relationship_target_type": target_type,
            "key": self.name,
            "title": self.name.capitalize(),
        }


class MultiselectField(Field):  # pylint: disable=too-few-public-methods
    """
    A field representing a multiselect with multiple options.

    Inherits from Field and allows multiple choices to be selected.
    """

    def __init__(self, name, choices):
        """
        Initializes a MultiselectField object.

        Args:
            name (str): The name of the multiselect field.
            choices (list): A list of selectable options.
        """
        super().__init__(name, "multiselect")
        self.choices = choices
