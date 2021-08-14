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
    path("accept_gp/<int:group_id>/<int:user_id>", views.acc_group_request, name="acc_group"),
    path("add_group_member/<int:group_id>", views.group_member_request, name="group_member"),
    path("done_group_member/<int:group_id>", views.done_group_member_request, name="done_group_member"),
    path("add_group/", views.add_group_request, name="add_group"),
    path("show_group/<int:group_id>/", views.show_group_request, name="show_group"),
    path("add_contact/", views.add_contact_request, name="add_contact"),
    path("expenses/", views.all_expenses, name="expenses"),
    path("pay/<int:cost_id/", views.pay, name='pay'),
    path("sendmail",views.sendmail)
]
