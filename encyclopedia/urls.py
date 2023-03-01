from django.urls import path

from . import views

app_name = 'encyclopedia'

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:title>", views.entry, name="entry"),
    path("search/", views.search, name="search"),
    path("random/", views.random,name="random"),
    path("new/", views.add_entry, name="add"),
    path("edit/<str:title>", views.edit_entry, name="edit")
]
