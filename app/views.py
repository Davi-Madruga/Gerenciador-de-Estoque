from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import ProdutoForm
from .models import Produto


@require_http_methods(["GET", "POST"])
def estoque(request):
    form = ProdutoForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("estoque")
    return render(request, "app/estoque.html", {
        "form": form, "produtos": Produto.objects.order_by("-id"),
    })
