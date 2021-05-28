from django.urls import path

from . import views

app_name = 'shaman'

urlpatterns = [
    path("webhook/<slug:token_slug>/", views.webhook, name="webhook")
]
