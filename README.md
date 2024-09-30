# Mercury Field Service (ORM Zendesk CustomObjects)

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
# add variables in .env or:
export ZENDESK_SUBDOMAIN=<your_zendesk_subdomain>.
export ZENDESK_API_TOKEN=<your_zendesk_api_token>.
export ZENDESK_EMAIL=<your_zendesk_email>.
```

## CRUD Operations with Records

Mercury Field Service ORM provides simple methods for performing CRUD (Create, Read, Update, Delete) operations on Zendesk custom object records. Below are examples of how to manage records in your custom objects.


### Creating a CustomObjects
```
class Produto(CustomObject):
    name = fields.TextField("name")
    referencia = fields.TextField("referencia")
    descricao = fields.TextareaField("descricao")
    garantia = fields.IntegerField("garantia")
    preco = fields.DecimalField("preco")
    ativo = fields.CheckboxField("ativo")
    voltagem = fields.DropdownField("voltagem", choices=["220", "110", "Bivolt"])
```

### Creating a Custom Object and Fields in Zendesk

Once you define the custom object class, you can create it in Zendesk using ZendeskObjectManager. This will automatically create the custom object and its fields in Zendesk.

```
from mercuryfieldservice.client.zendesk_manager import ZendeskObjectManager

# Create the custom object and fields in Zendesk
manager = ZendeskObjectManager(email="your-email@example.com")
manager.create_custom_object_from_model(Produto)
# or
manager.get_or_create_custom_object_from_model(Produto)
```
### Record Manager

Each custom object class is automatically assigned a RecordManager that handles interaction with the Zendesk API. The RecordManager allows you to:

- Create records: ```Produto.objects.create(**kwargs)```
- Get a single record: ```Produto.objects.get(id=1)```
- Filter records: ```Produto.objects.filter(ativo=True)```
- Delete records: ```Produto.objects.delete(id=1)```
- Retrieve all records: ```Produto.objects.all()```
  
### Creating a Record

You can create a new record by instantiating your custom object and calling the `save()` method:

```python
produto = Produto(name="Sample Product", referencia="12345", preco=99.99, ativo=True)
produto.save()

#or
Produto.objects.create(name="Sample Product", referencia="12345", preco=99.99, ativo=True)
```
### Retrieving a Record

You can retrieve an individual record by using the get() method:
```
retrieved_produto = Produto.objects.get(id=produto.id)
```
### Updating a Record

To update a record, modify its attributes and call the save() method again:
```
retrieved_produto.preco = 89.99
retrieved_produto.save()
```

### Deleting a Record

To delete a record from Zendesk, call the delete() method on the object:
```
retrieved_produto.delete()
```
## Querying and Filtering Records

You can retrieve all records or filter them based on certain criteria.
```
all_produtos = Produto.objects.all()
filtered_produtos = Produto.objects.filter(ativo=True)
last_object = Produto.objects.last()
```

