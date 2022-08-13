from typing import TYPE_CHECKING, Any, Callable, Coroutine, Hashable, Type, Union, cast

from django.apps import apps
from strawberry.types import Info

from strawberry_django_dataloaders.core.dataloader import BaseDataLoader

if TYPE_CHECKING:
    from django.db.models import Model as DjangoModel  # pragma: nocover


class BaseDataLoaderFactory:
    loader_class: Type["BaseDataLoader"]
    registered_dataloaders: dict[Hashable, Type["BaseDataLoader"]] = {}

    @classmethod
    def get_loader_class(cls, *args, **kwargs) -> Type["BaseDataLoader"]:
        """Generates dataloader classes at runtime when they are used the first time, later gets them from cache."""
        dataloader_key = cls.get_loader_key(*args, **kwargs)
        if dataloader_key not in cls.registered_dataloaders:
            loader_cls = cls._create_dataloader_cls(dataloader_key, *args, **kwargs)
            cls.registered_dataloaders[dataloader_key] = loader_cls
        return cls.registered_dataloaders[dataloader_key]

    @classmethod
    def _create_dataloader_cls(cls, dataloader_key: Hashable, *args, **kwargs) -> Type["BaseDataLoader"]:
        return cast(
            Type[BaseDataLoader],
            type(
                f"{dataloader_key}{cls.loader_class.__name__}",
                (cls.loader_class,),
                cls.get_loader_class_kwargs(*args, **kwargs),
            ),
        )

    @classmethod
    def get_loader_class_kwargs(cls, *args, **kwargs) -> dict:
        return kwargs

    @classmethod
    def get_loader_key(cls, *args, **kwargs) -> Hashable:
        """Return a unique key for the dataloader."""
        raise NotImplementedError  # pragma: nocover

    @classmethod
    def as_resolver(cls, *args, **kwargs) -> Callable[[Any, Info], Coroutine]:
        """
        Return a dataloader as a callable to be used in the field definition as a resolver.

        Example:
            @strawberry.django.type(models.User)
            class UserType:
                favourite_fruit = strawberry.django.field(resolver=<Factory>.as_resolver(args, kwargs))
        """
        raise NotImplementedError  # pragma: nocover


class BaseDjangoModelDataLoaderFactory(BaseDataLoaderFactory):
    @classmethod
    def get_loader_class(
        cls,
        model: Union[Type["DjangoModel"], str],  # Django model directly, or 'app_name.DjangoModel'
        /,  # forces 'model' to be positional argument
        **kwargs,
    ):
        if isinstance(model, str):
            model = apps.get_model(model)
        return super().get_loader_class(model, **kwargs)
