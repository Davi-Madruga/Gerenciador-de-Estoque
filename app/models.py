from django.core.validators import MaxValueValidator
from django.db import models


class Produto(models.Model):
    nome = models.CharField(max_length=120)
    quantidade = models.PositiveIntegerField(validators=[MaxValueValidator(2147483647)])

    class Meta:
        db_table = "produto"
