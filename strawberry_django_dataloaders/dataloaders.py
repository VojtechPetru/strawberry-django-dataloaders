from collections import defaultdict

from asgiref.sync import sync_to_async
from django.db.models import Model as DjangoModel

from strawberry_django_dataloaders.core.dataloader import BaseDjangoModelDataLoader


class BasicPKDataLoader(BaseDjangoModelDataLoader):
    """
    Base loader for simple PK relationship (e.g. get TravianAlliance of TravianAccount).

    EXAMPLE - load Travian alliance of TravianAccount:
        1. DATALOADER DEFINITION
        class BasicPKTravianAllianceDataLoader(BasicPKDataLoader):
            model = TravianAlliance

        2. USAGE
        @strawberry.django.type(models.TravianAccount)
        class TravianAccountType:
            ...

            @strawberry.field
            async def travian_alliance(self: "models.TravianAccount", info: "Info") -> list["TravianVillageType"]:
                return await BasicPKTravianAllianceDataLoader(context=info.context).load(self.travian_alliance_id)

    """

    @classmethod
    @sync_to_async
    def load_fn(cls, keys: list[str]) -> list[DjangoModel | None]:
        instances: list["DjangoModel"] = list(cls.model.objects.filter(pk__in=keys))
        # ensure instances are ordered in the same way as input 'keys'
        id_to_instance: dict[str, "DjangoModel"] = {inst.pk: inst for inst in instances}
        return [id_to_instance.get(id_) for id_ in keys]


class BasicReverseFKDataLoader(BaseDjangoModelDataLoader):
    """
    Base loader for reversed FK relationship (e.g. get BlogPosts of a User).

    EXAMPLE - load blog posts of account:
        1. DATALOADER DEFINITION
        class BlogPostsBasicReverseFKDataLoader(BasicReverseFKDataLoader):
            model = BlogPost
            reverse_path = 'user_id'

        2. USAGE
        @strawberry.django.type(models.User)
        class UserType:
            ...

            @strawberry.field
            async def blog_posts(self: "models.User", info: "Info") -> list["BlogPostType"]:
                return await BlogPostsBasicReverseFKDataLoader(context=info.context).load(self.pk)
    """

    reverse_path: str  # path to the 'parent' model from the reverse relationship

    @classmethod
    @sync_to_async
    def load_fn(cls, keys: list[str]) -> list[list[DjangoModel]]:
        instances: list["DjangoModel"] = list(cls.model.objects.filter(**{f"{cls.reverse_path}__in": keys}))
        # ensure that instances are ordered the same way as input 'ids'
        id_to_instances: dict[str, list["DjangoModel"]] = defaultdict(list)
        for instance in instances:
            id_to_instances[getattr(instance, cls.reverse_path)].append(instance)
        return [id_to_instances.get(key, []) for key in keys]
