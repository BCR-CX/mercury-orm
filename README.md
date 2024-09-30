# mercury-field-service

# Mercury Field Service

Mercury Field Service is a Python ORM (Object-Relational Mapping) designed to integrate seamlessly with the Zendesk Custom Objects API. It provides a Django-like interface for defining, managing, and interacting with Zendesk custom objects and records, simplifying the communication with Zendesk's API.

## Key Features

- **Custom Object Representation**: Define Zendesk custom objects using Python classes.
- **Automatic Record Management**: Built-in methods for creating, reading, updating, and deleting records via Zendesk's API.
- **Support for All Field Types**: Compatible with all Zendesk custom field types including text, dropdown, checkbox, date, integer, and more.
- **Automatic Object Creation**: Automatically create Zendesk custom objects and fields from Python class definitions.
- **Easy Record Operations**: Simple API to manage custom object records, with built-in support for querying, filtering, and pagination.

## Installation

```bash
pip install mercury-field-service

## Adicione as variáveis de ambiente
ZENDESK_SUBDOMAIN=<your_zendesk_subdomain>.

ZENDESK_API_TOKEN=<your_zendesk_api_token>.

ZENDESK_EMAIL=<your_zendesk_email>.

