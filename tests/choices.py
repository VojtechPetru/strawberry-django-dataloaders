from django.db.models import TextChoices


class UrlChoices(TextChoices):
    DATALOADERS = "graphql/dataloaders/"
    DATALOADER_FACTORIES = "graphql/dataloader-factories/"
    AUTO_DATALOADER_FIELDS = "graphql/auto-dataloader-fields/"
