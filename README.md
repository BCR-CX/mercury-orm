# Mercury (ORM Zendesk CustomObjects)

Mercury is a Python ORM (Object-Relational Mapping) designed to integrate seamlessly with the Zendesk Custom Objects API. It provides a Django-like interface for defining, managing, and interacting with Zendesk custom objects and records, simplifying the communication with Zendesk's API.

## Key Features

- **Custom Object Representation**: Define Zendesk custom objects using Python classes.
- **Automatic Record Management**: Built-in methods for creating, reading, updating, and deleting records via Zendesk's API.
- **Support for All Field Types**: Compatible with all Zendesk custom field types including text, dropdown, checkbox, date, integer, and more.
- **Automatic Object Creation**: Automatically create Zendesk custom objects and fields from Python class definitions.
- **Easy Record Operations**: Simple API to manage custom object records, with built-in support for querying, filtering, and pagination.

## Installation

```bash
pip install mercury-orm
# add variables in .env or:
export ZENDESK_SUBDOMAIN=<your_zendesk_subdomain>.
export ZENDESK_API_TOKEN=<your_zendesk_api_token>.
export ZENDESK_EMAIL=<your_zendesk_email>.
```

## CRUD Operations with Records

Mercury ORM provides simple methods for performing CRUD (Create, Read, Update, Delete) operations on Zendesk custom object records. Below are examples of how to manage records in your custom objects.


### Creating a CustomObjects
```
class Product(CustomObject):
    name = fields.TextField("name")
    code = fields.TextField("code")
    description = fields.TextareaField("description")
    price = fields.DecimalField("price")
    active = fields.CheckboxField("active")
    voltage = fields.DropdownField("voltage", choices=["220", "110", "Bivolt"])
```

### Creating a Custom Object and Fields in Zendesk

Once you define the custom object class, you can create it in Zendesk using ZendeskObjectManager. This will automatically create the custom object and its fields in Zendesk.

```
from mercuryorm.client.zendesk_manager import ZendeskObjectManager

# Create the custom object and fields in Zendesk
manager = ZendeskObjectManager(email="your-email@example.com")
manager.create_custom_object_from_model(Product)
# or
manager.get_or_create_custom_object_from_model(Product)
```
### Record Manager

Each custom object class is automatically assigned a RecordManager that handles interaction with the Zendesk API. The RecordManager allows you to:

- Create records: ```Product.objects.create(**kwargs)```
- Get a single record: ```Product.objects.get(id=1)```
- Filter records: ```Product.objects.filter(active=True)```
- Delete records: ```Product.objects.delete(id=1)```
- Retrieve all records: ```Product.objects.all()```

### Creating a Record

You can create a new record by instantiating your custom object and calling the `save()` method:

```python
product = Product(name="Sample Product", code="12345", price=99.99, active=True)
product.save()

#or
Product.objects.create(name="Sample Product", code="12345", price=99.99, active=True)
```
### Retrieving a Record

You can retrieve an individual record by using the get() method:
```
retrieved_product = Product.objects.get(id=product.id)
```
### Updating a Record

To update a record, modify its attributes and call the save() method again:
```
retrieved_product.price = 89.99
retrieved_product.save()
```

### Deleting a Record

To delete a record from Zendesk, call the delete() method on the object:
```
retrieved_product.delete()
```
## Querying and Filtering Records

You can retrieve all records or filter them based on certain criteria.
```
all_products = Product.objects.all()
filtered_products = Product.objects.filter(active=True)
last_object = Product.objects.last()
```
