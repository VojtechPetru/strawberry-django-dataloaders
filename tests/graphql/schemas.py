from functools import partial

import strawberry_django
import strawberry

from . import types


@strawberry.type
class DataLoadersQuery:
    fruits: list[types.FruitTypeDataLoaders] = strawberry_django.field()


@strawberry.type
class DataLoaderFactoriesQuery:
    fruits: list[types.FruitTypeDataLoaderFactories] = strawberry_django.field()


@strawberry.type
class AutoDataLoaderFieldsQuery:
    fruits: list[types.FruitTypeAutoDataLoaderFields] = strawberry_django.field()


_base_schema = partial(strawberry.Schema, mutation=None)
dataloaders_schema = _base_schema(query=DataLoadersQuery)
dataloader_factories_schema = _base_schema(query=DataLoaderFactoriesQuery)
auto_dataloader_fields_schema = _base_schema(query=AutoDataLoaderFieldsQuery)
