from django.urls import path

from strawberry_django_dataloaders.views import DataloaderAsyncGraphQLView

from . import choices
from .graphql import schemas

urlpatterns = [
    path(
        choices.UrlChoices.DATALOADERS.value,
        DataloaderAsyncGraphQLView.as_view(schema=schemas.dataloaders_schema),
    ),
    path(
        choices.UrlChoices.DATALOADER_FACTORIES.value,
        DataloaderAsyncGraphQLView.as_view(schema=schemas.dataloader_factories_schema),
    ),
    path(
        choices.UrlChoices.AUTO_DATALOADER_FIELDS.value,
        DataloaderAsyncGraphQLView.as_view(schema=schemas.auto_dataloader_fields_schema),
    ),
]
