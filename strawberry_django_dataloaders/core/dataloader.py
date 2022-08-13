from typing import TYPE_CHECKING, Type

from asgiref.sync import sync_to_async
from strawberry.dataloader import DataLoader

if TYPE_CHECKING:
    from django.db.models import Model as DjangoModel  # pragma: nocover

    from strawberry_django_dataloaders.views import DataloaderContext  # pragma: nocover


class BaseDataLoader(DataLoader):
    _instance_cache = None

    def __new__(cls, context: "DataloaderContext", force_new: bool = False) -> "BaseDataLoader":
        """
        Returns a dataloader instance.
        Takes the instance from request context cache or creates a new one if it does not exist there yet.
        This makes the dataloader "semi-singleton" in the sense that they are singleton in the context of each request.
        """
        if force_new or cls not in context.dataloaders:
            context.dataloaders[cls] = super().__new__(cls)
        return context.dataloaders[cls]

    def __init__(self, context: "DataloaderContext", **kwargs):
        if self._instance_cache is None:
            self._instance_cache = context.dataloaders[self.__class__]
        super().__init__(**kwargs)


class BaseDjangoModelDataLoader(BaseDataLoader):
    model: Type["DjangoModel"] = NotImplemented

    def __init__(self, *args, **kwargs):
        super().__init__(*args, load_fn=self.load_fn, **kwargs)

    @classmethod
    @sync_to_async
    def load_fn(cls, keys: list[str]):
        raise NotImplementedError  # pragma: nocover
