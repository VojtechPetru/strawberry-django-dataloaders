import strawberry
import strawberry_django
from strawberry.types import Info

from .. import models
from strawberry_django_dataloaders import factories
from strawberry_django_dataloaders import fields
from . import dataloaders


@strawberry_django.type(models.FruitVariety)
class FruitVarietyType:
    id: strawberry.auto
    name: strawberry.auto


@strawberry_django.type(models.FruitPlant)
class FruitPlantType:
    name: strawberry.auto
    fruit: strawberry.auto


@strawberry_django.type(models.Color)
class ColorType:
    name: strawberry.auto
    fruits: strawberry.auto


@strawberry_django.type(models.FruitEater)
class FruitEaterType:
    name: strawberry.auto
    favourite_fruit: strawberry.auto


@strawberry_django.type(models.Fruit)
class FruitTypeDataLoaders:
    """Uses the simplest form of dataloaders."""
    id: strawberry.auto
    name: strawberry.auto

    @strawberry.field
    async def color(self: "models.Fruit", info: "Info") -> ColorType | None:
        return await dataloaders.ColorPKDataLoader(context=info.context).load(self.color_id)

    @strawberry.field
    async def plant(self: "models.Fruit", info: "Info") -> FruitPlantType | None:
        return await dataloaders.FruitPlantPKDataLoader(context=info.context).load(self.plant_id)

    @strawberry.field
    async def eaters(self: "models.Fruit", info: "Info") -> list[FruitEaterType]:
        return await dataloaders.FruitEatersReverseFKDataLoader(context=info.context).load(self.pk)


@strawberry_django.type(models.Fruit)
class FruitTypeDataLoaderFactories:
    """Uses dataloader factories."""
    id: strawberry.auto
    name: strawberry.auto

    @strawberry.field
    async def color(self: "models.Fruit", info: "Info") -> ColorType | None:
        loader = factories.PKDataLoaderFactory.get_loader_class('tests.Color')
        return await loader(context=info.context).load(self.color_id)

    @strawberry.field
    async def plant(self: "models.Fruit", info: "Info") -> FruitPlantType | None:
        loader = factories.PKDataLoaderFactory.get_loader_class('tests.FruitPlant')
        return await loader(context=info.context).load(self.plant_id)

    @strawberry.field
    async def eaters(self: "models.Fruit", info: "Info") -> list[FruitEaterType]:
        loader = factories.ReverseFKDataLoaderFactory.get_loader_class(
            'tests.FruitEater',
            reverse_path='favourite_fruit_id',
        )
        return await loader(context=info.context).load(self.color_id)

    # @strawberry.field  # TODO is M2M - need to create dataloader & factory for such relation
    # async def types(self: "models.Fruit", info: "Info") -> list["ColorType"]:
    #     loader = factories.PKDataLoaderFactory.get_loader_class('tests.Color')
    #     return await loader(context=info.context).load(self.color_id)


@strawberry_django.type(models.Fruit)
class FruitTypeAutoDataLoaderFields:
    """Uses auto dataloader fields."""
    id: strawberry.auto
    name: strawberry.auto
    color: ColorType = fields.auto_dataloader_field()
    plant: FruitPlantType = fields.auto_dataloader_field()
    varieties: list[FruitVarietyType] = fields.auto_dataloader_field()
    eaters: list[FruitEaterType] = fields.auto_dataloader_field()
