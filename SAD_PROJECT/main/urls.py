from django.urls import path

from . import views

app_name = "main"

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("register/", views.register_request, name="register"),
    path("report/", views.report, name="report"),
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
    path("expenses_report/<int:user_id>/", views.report_expenses, name="report_exp"),
    path("pay/<int:cost_id>/", views.pay, name='pay'),
    path("edit/", views.edit_profile, name='edit_profile'),
    path("accept_contact/<int:me>/<int:sec_id>", views.accept_contact, name='accept_contact'),
    path("add_share/<int:group_id>/", views.add_share, name='add_share'),
    path("add_share_member/<int:group_id>/<int:share_id>/", views.add_share_member, name='add_share_member'),
    path("end_share_member/<int:group_id>/<int:share_id>/", views.end_share_member, name='end_share'),
]
