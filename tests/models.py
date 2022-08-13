from django.db import models


class BaseTestModel(models.Model):
    name = models.CharField(max_length=32)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Fruit(BaseTestModel):
    plant = models.OneToOneField("FruitPlant", on_delete=models.SET_NULL, null=True)
    color = models.ForeignKey("Color", null=True, blank=True, related_name="fruits", on_delete=models.CASCADE)
    varieties = models.ManyToManyField("FruitVariety", related_name="fruits")


class FruitPlant(BaseTestModel):
    pass


class FruitEater(BaseTestModel):
    favourite_fruit = models.ForeignKey("Fruit", null=True, on_delete=models.SET_NULL, related_name="eaters")


class FruitVariety(BaseTestModel):
    pass


class Color(BaseTestModel):
    pass
