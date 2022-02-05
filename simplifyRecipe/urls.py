from django.urls import path
from . import views

urlpatterns = [
    path('', views.simplify_recipe, name='simplify_recipe'),
]