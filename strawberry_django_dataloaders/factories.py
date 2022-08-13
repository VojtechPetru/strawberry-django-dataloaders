from typing import Callable, Coroutine, Type

from django.db.models import ManyToOneRel
from django.db.models import Model as DjangoModel
from django.db.models.fields.related import RelatedField
from strawberry.types import Info
from strawberry_django.fields.field import StrawberryDjangoField

from .core.factory import BaseDjangoModelDataLoaderFactory
from .dataloaders import BasicPKDataLoader, BasicReverseFKDataLoader


class PKDataLoaderFactory(BaseDjangoModelDataLoaderFactory):
    """
    Base factory for simple PK relationship dataloaders. For example, get favourite fruit (Fruit model) of a User.

    EXAMPLE:
        CONSIDER DJANGO MODELS:
            class Fruit(models.Model):
                ...

            class User(models.Model):
                favourite_fruit = models.ForeignKey("Fruit", ...)

        THE FACTORY WOULD BE USED IN A FOLLOWING MANNER:
            @strawberry.django.type(models.User)
            class UserType:
                ...
                @strawberry.field
                async def favourite_fruit(self: "models.User", info: "Info") -> "FruitType":
                    loader = BasicPKDataLoaderFactory.get_loader_class('<django_app>.Fruit')
                    return await loader(context=info.context).load(self.favourite_fruit_id)
    """

    loader_class = BasicPKDataLoader

    @classmethod
    def get_loader_key(cls, model: Type["DjangoModel"], **kwargs):
        return model

    @classmethod
    def get_loader_class_kwargs(cls, model: Type["DjangoModel"], **kwargs):
        return {
            "model": model,
        }

    @classmethod
    def as_resolver(cls) -> Callable[["DjangoModel", Info], Coroutine]:
        async def resolver(root: "DjangoModel", info: "Info"):  # beware, first argument needs to be called 'root'
            field_data: "StrawberryDjangoField" = info._field
            relation: "RelatedField" = root._meta.get_field(field_name=field_data.django_name)
            pk = getattr(root, relation.attname)
            return await cls.get_loader_class(field_data.django_model)(context=info.context).load(pk)

        return resolver


class ReverseFKDataLoaderFactory(BaseDjangoModelDataLoaderFactory):
    """
    Base factory for reverse FK relationship dataloaders. For example, get blog posts of a User.

    EXAMPLE:
        CONSIDER DJANGO MODELS:
            class User(models.Model):
                ...

            class BlogPost(models.Model):
                published_by = models.ForeignKey("User", ...)

        THE FACTORY WOULD BE USED IN A FOLLOWING MANNER:
            @strawberry.django.type(models.User)
            class UserType:
                ...
                @strawberry.field
                async def blog_posts(self: "models.User", info: "Info") -> list["BlogPostType"]:
                    loader = BasicReverseFKDataLoaderFactory.get_loader_class(
                        '<app_name>.BlogPost',
                        reverse_path='published_by_id',
                    )
                    return await loader(context=info.context).load(self.pk)
    """

    loader_class = BasicReverseFKDataLoader

    @classmethod
    def get_loader_key(cls, model: Type["DjangoModel"], **kwargs):
        reverse_path = kwargs.get("reverse_path")
        if not reverse_path:
            raise ValueError(f"{cls.__name__}: 'reverse_path' not specified for reverse relation of {model.__name__}.")
        return f"{model}-{reverse_path}"

    @classmethod
    def get_loader_class_kwargs(cls, model: Type["DjangoModel"], **kwargs):
        return {
            "model": model,
            "reverse_path": kwargs["reverse_path"],
        }

    @classmethod
    def as_resolver(cls) -> Callable[["DjangoModel", Info], Coroutine]:
        async def resolver(root: "DjangoModel", info: "Info"):  # beware, first argument needs to be called 'root'
            field_data: "StrawberryDjangoField" = info._field
            relation: "ManyToOneRel" = root._meta.get_field(field_name=field_data.django_name)
            loader = cls.get_loader_class(field_data.django_model, reverse_path=relation.field.attname)
            return await loader(context=info.context).load(root.pk)

        return resolver
