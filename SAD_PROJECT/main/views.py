from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import loader
from django.urls import reverse

from SAD_PROJECT import settings
from group.models import Group, GroupForm
from .forms import NewUserForm, ShareForm, EditForm
from .models import Account, Contact, Expense, Address, Share
from django.core.mail import send_mail



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


def accept_contact(request, me, sec_id):
    me = Account.get_account_by_user(me)
    sec_user = Account.get_account_by_user(sec_id)
    Contact.add_contact(me, sec_user)
    return HttpResponseRedirect(reverse('main:homepage', args=()))


def add_contact_request(request):  # send a form
    if request.method == "POST":
        checked_id = request.POST.getlist('tag')
        for id in checked_id:
            me = Account.get_account_by_user(request.user.id)
            sec_user = Account.get_account_by_user(id)
            print('click http://127.0.0.1:8000/accept_contact/' + str(request.user.id) + '/' + str(id))
            print("----------------")
            result = send_mail('Contact with ' + me.user.username,
                               'click http://127.0.0.1:8000/accept_contact/' + str(request.user.id) + '/' + str(id),
                               settings.EMAIL_HOST_USER,
                               [sec_user.user.email]
                               )
            print(result)
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
        result = send_mail('Inviting Group',
                           'click http://127.0.0.1:8000/accept_gp/' + str(group_id) + '/' + str(acc.user.id),
                           settings.EMAIL_HOST_USER,
                           [acc.user.email]
                           )
        print(result)
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
    context = {'members': gp.get_members(gp), 'group_id': group_id,
               'shares': Share.get_shares_for_gp(group_id)}
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


def report(request):
    template = loader.get_template('main/report.html')
    l = Account.objects.all()
    context = {'users': [i.serializer_2() for i in l]}
    return HttpResponse(template.render(context, request))
    pass


def all_expenses(request):
    template = loader.get_template('main/expenses.html')
    acc = Account.get_account_by_user(request.user.id)
    context = {'payed_payer': Expense.get_payed_payer_expenses(acc),
               'payed_debtor': Expense.get_payed_debtor_expenses(acc),
               'not_payed': Expense.get_not_payed_expenses(acc),
               'friend_not_payed': Expense.get_friend_not_payed_expenses(acc),
               'with_url': True}
    return HttpResponse(template.render(context, request))


def report_expenses(request, user_id):
    template = loader.get_template('main/expenses.html')
    acc = Account.get_account_by_user(user_id)
    context = {'payed': Expense.get_payed_expenses(acc),
               'not_payed': Expense.get_not_payed_expenses(acc),
               'friend_not_payed': Expense.get_friend_not_payed_expenses(acc),
               'with_url': False}
    return HttpResponse(template.render(context, request))


def pay(request, cost_id):
    if not request.user.is_authenticated:
        template = loader.get_template('main/index.html')
        context = {}
        return HttpResponse(template.render(context, request))
    else:
        acc = Account.get_account_by_user(request.user.id)
        err = Expense.pay_expenses(cost_id, acc)
        if err is None:
            return HttpResponseRedirect(reverse('main:expenses'))
        return HttpResponseRedirect(reverse('main:expenses'))


def edit_profile(request):
    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            addr = form.cleaned_data['address']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            country = form.cleaned_data['country']
            phone_number = form.cleaned_data['phone_number']
            my_user = Account.get_account_by_user(request.user.id)
            my_user.phone_number = phone_number
            a = Address(address=addr, city=city, state=state, country=country)
            a.save()
            my_user.address = a
            my_user.save()
            return redirect("main:homepage")
    else:
        form = EditForm()
    return render(request, 'main/edit_profile.html', {'form': form})


def add_share(request, group_id):
    gp = Group.get_group(group_id)
    if request.method == 'POST':
        form = ShareForm(request.POST)
        form.edit(my_choices=gp.get_members(gp, True))
        if form.is_valid():
            name = form.cleaned_data['name']
            addr = form.cleaned_data['address']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            country = form.cleaned_data['country']
            a = Address(address=addr, city=city, state=state, country=country)
            a.save()
            credit = form.cleaned_data['credit']
            image = form.cleaned_data.get('image')
            date = form.cleaned_data['date']
            c_id = form.cleaned_data['creditor']
            print(c_id)
            share = Share(name=name, date=date, address=a, image=image, credit=credit, group_id=group_id,
                          creditor=Account.get_account_by_user(c_id))
            share.save()
            return HttpResponseRedirect(reverse('main:add_share_member', args=(group_id, share.pk)))
    else:
        form = ShareForm()
        form.edit(my_choices=gp.get_members(gp, True))
    return render(request, 'main/add_share.html', {
        'form': form,
        'group_id': group_id
    })


def add_share_member(request, group_id, share_id):
    if request.method == 'POST':
        acc_id = request.POST['accounts']
        percent = request.POST['percent']
        Share.add_shares(share_id, Account.get_account_by_user(acc_id), percent)
    gp = Group.get_group(group_id)
    return render(request, 'main/share_member.html',
                  {'users': gp.get_members(gp),
                   'group_id': group_id,
                   'share_id': share_id
                   })


def end_share_member(request, group_id, share_id):
    if request.method == 'POST':
        acc_id = request.POST['accounts']
        percent = request.POST['percent']
        Share.add_shares(share_id, Account.get_account_by_user(acc_id), percent)
    Share.get_share_by_id(share_id).build_expenses()
    return HttpResponseRedirect(reverse('main:show_group', args=(group_id,)))
