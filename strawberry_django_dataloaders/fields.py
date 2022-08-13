from typing import TYPE_CHECKING, Any

import strawberry.django
from strawberry import UNSET

from . import exceptions, factories

if TYPE_CHECKING:
    from django.db.models import Model as DjangoModel  # pragma: nocover
    from django.db.models.fields.related import RelatedField  # pragma: nocover
    from strawberry.types import Info  # pragma: nocover
    from strawberry_django.fields.field import StrawberryDjangoField  # pragma: nocover


async def get_dataloader_resolver(root: "DjangoModel", info: "Info"):
    field_data: "StrawberryDjangoField" = info._field
    relation: "RelatedField" = root._meta.get_field(field_name=field_data.django_name)
    if relation.many_to_one or relation.one_to_one:
        return await factories.PKDataLoaderFactory.as_resolver()(root, info)
    elif relation.one_to_many:
        return await factories.ReverseFKDataLoaderFactory.as_resolver()(root, info)
    else:
        raise exceptions.UnsupportedRelationError(f"Unsupported relation on {relation.__repr__()}.")


def auto_dataloader_field(
    resolver=get_dataloader_resolver,
    *,
    name=None,
    field_name=None,
    filters=UNSET,
    default=UNSET,
    **kwargs,
) -> Any:
    """
    A field which has automatic dataloader resolver based on the relationship type (one-to-one, one-to-many, etc.).

    EXAMPLE:
        CONSIDER DJANGO MODELS:
            class Fruit(BaseTestModel):
                plant = models.OneToOneField("FruitPlant", ...)
                color = models.ForeignKey("Color", related_name="fruits", ...)
                varieties = models.ManyToManyField("FruitVariety", related_name="fruits")

            class FruitEater(BaseTestModel):
                favourite_fruit = models.ForeignKey("Fruit", related_name="eaters", ...)

        DEFINE THE STRAWBERRY TYPE AS:
            @strawberry_django.type(models.Fruit)
            class FruitTypeAutoDataLoaderFields:
                plant: FruitPlantType = fields.auto_dataloader_field()
                color: ColorType = fields.auto_dataloader_field()
                varieties: list[FruitVarietyType] = fields.auto_dataloader_field()
                eaters: list[FruitEaterType] = fields.auto_dataloader_field()
    """
    return strawberry.django.field(
        resolver=resolver,
        name=name,
        field_name=field_name,
        filters=filters,
        default=default,
        **kwargs,
    )
