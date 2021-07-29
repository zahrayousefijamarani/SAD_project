from django.urls import path

from . import views

app_name = "main"

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("register/", views.register_request, name="register"),
    path("login/", views.login_request, name="login"),
    path("logout/", views.logout_request, name="logout"),
    path("contacts/", views.contact_request, name="contacts"),
    path("group/", views.group_request, name="group"),
]
