from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.template import loader


def index(request):
    template = loader.get_template('SAD/index.html')
    context = {}
    return HttpResponse(template.render(context, request))


def login_page(request):
    template = loader.get_template('SAD/login.html')
    context = {}
    return HttpResponse(template.render(context, request))


def signup_page(request):
    template = loader.get_template('SAD/signup.html')
    context = {}
    return HttpResponse(template.render(context, request))
