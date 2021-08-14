from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import loader
from django.urls import reverse

from .forms import NewUserForm
from .models import Account, Contact, Expense
from group.models import Group, GroupForm


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
    acc = Account.get_account_by_user(request.user.id)
    context = {'contacts': Contact.get_contacts(acc)}
    return HttpResponse(template.render(context, request))


def add_contact_request(request):  # send a form
    if request.method == "POST":
        checked_id = request.POST.getlist('tag')
        for id in checked_id:
            Contact.add_contact(Account.get_account_by_user(request.user.id), Account.get_account_by_user(id))
        return HttpResponseRedirect(reverse('main:contacts', args=()))

    else:
        template = loader.get_template('main/add_contact.html')
        all_account = Account.get_all_accounts()
        c = Contact.get_contacts(Account.get_account_by_user(request.user.id))
        contacts = list([i['id'] for i in c])
        accounts = []
        for acc in all_account:
            if not (acc['id'] == request.user.id or acc['id'] in contacts):
                accounts.append(acc)

        context = {'users': accounts}
        return HttpResponse(template.render(context, request))


def group_request(request):
    template = loader.get_template('main/group.html')
    acc = Account.get_account_by_user(request.user.id)
    context = {'groups': Group.get_all_group(acc)}
    return HttpResponse(template.render(context, request))


def group_member_request(request, group_id):
    template = loader.get_template('main/choose_member.html')
    acc = Account.get_account_by_user(request.user.id)
    context = {'contacts': Contact.get_contacts(acc),
               'g_id': group_id}
    return HttpResponse(template.render(context, request))


def acc_group_request(request, group_id, user_id):
    Group.add_members(group_id, [user_id])
    return HttpResponseRedirect(reverse('main:homepage', args=()))


def done_group_member_request(request, group_id):
    checked_id = request.POST.getlist('tag')
    for id in checked_id:
        acc = Account.get_account_by_user(id)
        print(acc.user.email)
        print('click http://127.0.0.1:8000/accept_gp/' + str(group_id) + '/' + str(acc.user.id))
        print("----------------")
        # result = EmailSender().send_email([acc.user.email],
        #                                   'Inviting Group',
        #                                   'click 127.0.0.1:8000/accept_gp/' + str(group_id) + '/' + str(acc.user.id),
        #                                   'main/home.html',
        #                                   'click 127.0.0.1:8000/accept_gp/' + str(group_id) + '/' + str(acc.user.id))
        # print(result)
    return HttpResponseRedirect(reverse('main:show_group', args=(group_id,)))


def add_group_request(request):  # send a form
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('group_name')
            pk = Group.create_group(name, Account.get_account_by_user(request.user.id))
            return HttpResponseRedirect(reverse('main:group_member', args=(pk,)))
        else:
            messages.error(request, "Invalid name")
    else:
        form = GroupForm()
    return render(request, 'main/add_group.html', {'form': form})


def show_group_request(request, group_id):
    template = loader.get_template('main/specific_group.html')
    gp = Group.get_group(group_id)
    context = {'members': gp.get_members(gp)}
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


def all_expenses(request):
    template = loader.get_template('main/expenses.html')
    acc = Account.get_account_by_user(request.user.id)
    context = {'expenses': Expense.get_all_expenses(acc)}
    return HttpResponse(template.render(context, request))


def pay(request, cost_id):
    # pay this cost id form wallet and add to receiver
    pass
