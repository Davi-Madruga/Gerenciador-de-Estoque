from django import forms

from .models import Produto


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ["nome", "quantidade"]
        labels = {"nome": "Nome do produto"}
        widgets = {"nome": forms.TextInput(attrs={"pattern": r".*\S.*"}),
                   "quantidade": forms.NumberInput(attrs={"min": 0, "max": 2147483647, "step": 1})}
