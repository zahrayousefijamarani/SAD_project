from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader

from .forms import NewUserForm
from .models import Account


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            Account.new_account(user)
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("main:homepage")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="main/register.html", context={"register_form": form})


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("main:homepage")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="main/login.html", context={"login_form": form})


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("main:homepage")


def contact_request(request):
    template = loader.get_template('main/contacts.html')
    context = {}
    return HttpResponse(template.render(context, request))


def group_request(request):
    template = loader.get_template('main/group.html')
    context = {}
    return HttpResponse(template.render(context, request))


def homepage(request):
    if not request.user.is_authenticated:
        template = loader.get_template('main/index.html')
        context = {}
        return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template('main/home.html')
        acc = Account.get_account_by_user(request.user.id)
        context = acc.serializer()
        return HttpResponse(template.render(context, request))
