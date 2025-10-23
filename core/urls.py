from django.urls import path
from .views import PromailListView

app_name="core"

urlpatterns=[
    path("", PromailListView.as_view(), name="main"),
]
