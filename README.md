# Dataloaders for Django and Strawberry
A set of tools for using dataloaders with [Django](https://github.com/django/django) 
and [Strawberry](https://github.com/strawberry-graphql/strawberry) without unnecessary boilerplate.

## Installation

```bash
pip install strawberry-django-dataloaders
```


# Usage & examples
This package provides 3 levels of generating dataloaders, each offering higher level of abstraction
than the previous one.

### View
In the `graphql/` endpoint where you wish to use dataloaders, use (or subclass) `DataloaderAsyncGraphQLView`.
This is necessary because created dataloaders are stored to the request context. This ensures that:

- fresh dataloader instances are created for each request
- a dataloader persists for the duration of the request

which are both important properties for loaded values caching.

```python
from django.urls import path

from strawberry_django_dataloaders.views import DataloaderAsyncGraphQLView

urlpatterns = [
    path('graphql/', DataloaderAsyncGraphQLView.as_view(schema=...)),
]
```

### Models definition
Definition of models used in the examples.
```python
from django.db import models

class Fruit(models.Model):
    plant = models.OneToOneField("FruitPlant", ...)
    color = models.ForeignKey("Color", ...)
    varieties = models.ManyToManyField("FruitVariety", ..., related_name="fruits")

class FruitEater(models.Model):
    favourite_fruit = models.ForeignKey("Fruit", ..., related_name="eaters")
```
### Level 1: Simple dataloader
On the first level, we're defining and using different dataloader for each relationship.
#### One-to-one and Many-to-one relationship
1. Define the dataloaders
```python
from strawberry_django_dataloaders import dataloaders

class ColorPKDataLoader(dataloaders.BasicPKDataLoader):
    model = models.Color


class FruitPlantPKDataLoader(dataloaders.BasicPKDataLoader):
    model = models.FruitPlant
```
2. Use them when defining the Strawberry type
```python
@strawberry_django.type(models.Fruit)
class FruitType:
    id: strawberry.auto
    
    ### ↓ HERE ↓ ###
    @strawberry.field
    async def color(self: "models.Fruit", info: "Info") -> ColorType | None:
        return await dataloaders.ColorPKDataLoader(context=info.context).load(self.color_id)

    @strawberry.field
    async def plant(self: "models.Fruit", info: "Info") -> FruitPlantType | None:
        return await dataloaders.FruitPlantPKDataLoader(context=info.context).load(self.plant_id)
```

#### One-to-many relationship
1. Define the dataloader
```python
from strawberry_django_dataloaders import dataloaders

class FruitEatersReverseFKDataLoader(dataloaders.BasicReverseFKDataLoader):
    model = models.FruitEater
    reverse_path = "favourite_fruit_id"   # <-- is the "reverse" FK field from FruitEater to Fruit model
```
2. Use it when defining the Strawberry type
```python
@strawberry_django.type(models.Fruit)
class FruitType:
    id: strawberry.auto
    
    ### ↓ HERE ↓ ###
    @strawberry.field
    async def eaters(self: "models.Fruit", info: "Info") -> list[FruitEaterType]:
        return await dataloaders.FruitEatersReverseFKDataLoader(context=info.context).load(self.pk)
```

### Level 2: Dataloader factories
When using the dataloader factories, we no longer need to define a dataloader for each relation.
```python
from strawberry_django_dataloaders import factories


@strawberry_django.type(models.Fruit)
class FruitTypeDataLoaderFactories:
    id: strawberry.auto
    
    ### ↓ ONE-TO-ONE AND MANY-TO-ONE DATALOADERS ↓ ###
    @strawberry.field
    async def color(self: "models.Fruit", info: "Info") -> ColorType | None:
        loader = factories.PKDataLoaderFactory.get_loader_class("tests.Color")
        return await loader(context=info.context).load(self.color_id)

    @strawberry.field
    async def plant(self: "models.Fruit", info: "Info") -> FruitPlantType | None:
        loader = factories.PKDataLoaderFactory.get_loader_class("tests.FruitPlant")
        return await loader(context=info.context).load(self.plant_id)
    
    ### ↓ ONE-TO-MANY DATALOADER ↓ ###
    @strawberry.field
    async def eaters(self: "models.Fruit", info: "Info") -> list[FruitEaterType]:
        loader = factories.ReverseFKDataLoaderFactory.get_loader_class(
            "tests.FruitEater",
            reverse_path="favourite_fruit_id",
        )
        return await loader(context=info.context).load(self.color_id)
```

### Level 3: Auto dataloader field
A field used in a similar fashion as native Django strawberry field, but it has auto-defined correct dataloader handler
based on the field relationship.
```python
from strawberry_django_dataloaders import fields 

@strawberry_django.type(models.Fruit)
class FruitTypeAutoDataLoaderFields:
    id: strawberry.auto
    color: ColorType = fields.auto_dataloader_field()
    plant: FruitPlantType = fields.auto_dataloader_field()
    varieties: list[FruitVarietyType] = fields.auto_dataloader_field()
    eaters: list[FruitEaterType] = fields.auto_dataloader_field()
```

## Contributing
Pull requests for any improvements are welcome.

[Poetry](https://github.com/sdispater/poetry) is used to manage dependencies.
To get started follow these steps:

```shell
git clone https://github.com/VojtechPetru/strawberry-django-dataloaders
cd strawberry-django-dataloaders
poetry install
poetry run pytest
```

### Pre commit

We have a configuration for
[pre-commit](https://github.com/pre-commit/pre-commit), to add the hook run the
following command:

```shell
pre-commit install
```

## Links
- Inspired and builds on top of a great article at: https://alexcleduc.com/posts/graphql-dataloader-composition/
- Repository: https://github.com/VojtechPetru/strawberry-django-dataloaders
- Issue tracker: https://github.com/VojtechPetru/strawberry-django-dataloaders/issues. 
In case of sensitive bugs (e.g. security vulnerabilities) please contact me at _petru.vojtech@gmail.com_ directly.

## Known issues/shortcomings
- `Many-to-many` relation is currently not supported.
