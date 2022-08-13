from dataclasses import dataclass, field
from typing import Callable, Coroutine, Any, Type

import pytest
from django.http import HttpResponse
from django.test import AsyncClient

from . import models
from .tests import fixtures
from .tests.fixtures import BaseResponseFixture
from .tests.gql_queries import GQLQueries


@dataclass
class DbData:
    fruits: list[models.Fruit] = field(default_factory=list)
    colors: list[models.Color] = field(default_factory=list)
    eaters: list[models.FruitEater] = field(default_factory=list)
    varieties: list[models.FruitVariety] = field(default_factory=list)


@dataclass
class TestCollection:
    """A basic connection between the query, state of db and expected response in a test."""
    query: GQLQueries
    db_data: DbData
    exp_response: Type[BaseResponseFixture]


@pytest.fixture
def db_data(db) -> DbData:
    """Generate some default db data."""
    fruit_names = ["strawberry", "raspberry", "banana"]
    fruit_plant_names = ["strawberry plant", "raspberry plant", None]
    color_names = ["red", "yellow", "orange"]
    eater_names = ['pepa', 'josef']
    data = DbData()
    for fruit_name, plant_name, color_name in zip(fruit_names, fruit_plant_names, color_names):
        color = models.Color.objects.create(name=color_name)
        plant = models.FruitPlant.objects.create(name=plant_name) if plant_name else None
        data.fruits.append(models.Fruit.objects.create(name=fruit_name, color=color, plant=plant))
        data.colors.append(color)

    data.eaters = [models.FruitEater.objects.create(name=name, favourite_fruit=data.fruits[0]) for name in eater_names]
    return data


@pytest.fixture
def arequest(async_client: AsyncClient) -> Callable[[GQLQueries, str], Coroutine[HttpResponse, Any, Any]]:
    async def make_request(query: GQLQueries, url: str):
        return await async_client.post(f"/{url}", data={'query': query}, content_type='application/json')
    return make_request


@pytest.fixture
def baseline_collection(db_data: DbData) -> TestCollection:
    collection = TestCollection(
        query=GQLQueries.FRUITS_DATALOADERS,
        exp_response=fixtures.FruitsResponseFixture,
        db_data=db_data,
    )
    return collection


@pytest.fixture
def empty_db_collection() -> TestCollection:
    collection = TestCollection(
        query=GQLQueries.FRUITS_DATALOADERS,
        exp_response=fixtures.FruitsResponseEmptyDbFixture,
        db_data=DbData(),
    )
    return collection
