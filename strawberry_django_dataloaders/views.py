from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Type

from strawberry.django.context import StrawberryDjangoContext
from strawberry.django.views import AsyncGraphQLView

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse  # pragma: nocover

    from strawberry_django_dataloaders.core.dataloader import BaseDataLoader  # pragma: nocover


@dataclass
class DataloaderContext(StrawberryDjangoContext):
    dataloaders: dict[Type["BaseDataLoader"], "BaseDataLoader"] = field(default_factory=dict)


class DataloaderAsyncGraphQLView(AsyncGraphQLView):
    async def get_context(self, request: "HttpRequest", response: "HttpResponse") -> DataloaderContext:
        context: "StrawberryDjangoContext" = await super().get_context(request, response)
        return DataloaderContext(**context.__dict__)
