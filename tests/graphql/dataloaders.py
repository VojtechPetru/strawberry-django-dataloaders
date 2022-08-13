from strawberry_django_dataloaders import dataloaders
from .. import models


class ColorPKDataLoader(dataloaders.BasicPKDataLoader):
    model = models.Color


class FruitPlantPKDataLoader(dataloaders.BasicPKDataLoader):
    model = models.FruitPlant


class FruitEatersReverseFKDataLoader(dataloaders.BasicReverseFKDataLoader):
    model = models.FruitEater
    reverse_path = 'favourite_fruit_id'
