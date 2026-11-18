from django.contrib import admin
from django.urls import path

from app.views import estoque

urlpatterns = [
    path("", estoque, name="estoque"),
    path("admin/", admin.site.urls),
]
