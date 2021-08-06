import random
import string

from django.contrib.auth.models import User
from django.db import models
from django import forms

ID_FIELD_LENGTH = 16
alphabet = string.ascii_lowercase + string.digits


def random_id(length):
    def byte_to_base32_chr(byte):
        return alphabet[byte & 31]

    random_bytes = [random.randint(0, 0xFF) for i in range(length)]
    return ''.join(map(byte_to_base32_chr, random_bytes))


# Create your models here
class Wallet(models.Model):
    credit = models.CharField(max_length=10, default=0)


class Transaction(models.Model):
    date = models.DateField(auto_now=True)
    description = models.CharField(max_length=100)
    payment_type = models.CharField(max_length=100)
    cash_amount = models.CharField(max_length=10)
    wallet = models.ForeignKey(Wallet, related_name='transactions', on_delete=models.CASCADE)


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, related_name='accounts', on_delete=models.CASCADE)
    access_final_date = models.DateField(verbose_name='تاریخ انقضای token', auto_now=True)
    uid = models.CharField(max_length=ID_FIELD_LENGTH, null=False, blank=False, unique=True, verbose_name='آیدی یکتا')

    @classmethod
    def generate_uid(cls):
        while True:
            random_unique_id = random_id(ID_FIELD_LENGTH)
            try:
                cls.objects.get(uid=random_unique_id)
            except:
                return random_unique_id

    def serializer(self, random_key=None):

        return {
            'uid': self.uid, 'username': self.user.username, 'email': self.user.email, 'credit': self.wallet.credit
        }

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = Account.generate_uid()

        return super(Account, self).save(*args, **kwargs)

    @classmethod
    def get_account_by_user(cls, user_id):
        return cls.objects.get(user__id=user_id)

    @classmethod
    def new_account(cls, user):
        w = Wallet()
        w.save()
        acc = Account(user=user, wallet=w)
        acc.save()

    @staticmethod
    def get_account_by_user(user_id):
        return Account.objects.get(user__id=user_id)


class Contact(models.Model):
    account = models.ForeignKey(Account, related_name="contacts", on_delete=models.CASCADE, null=False)
    contact_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=False)

    def serializer(self):
        return {
            'name': self.contact_account.user.username, 'email': self.contact_account.user.email,
            'id': self.contact_account.uid
        }

    @classmethod
    def add_contact(cls, s, d):
        if s is None or d is None:
            return
        c = Contact(account=s, contact_account=d)
        c.save()

    @classmethod
    def get_contacts(cls, account):
        if account is None:
            return []
        list_of_contacts = cls.objects.filter(account=account)
        return [i.serializer() for i in list_of_contacts]


class Group(models.Model):
    group_name = models.CharField(max_length=250)
    admin = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="admin_account")
    members = models.ManyToManyField(Account, related_name="member_accounts")

    @staticmethod
    def create_group(name, admin):
        if name == "" or admin is None:
            return
        g = Group(group_name=name, admin=admin)
        g.save()
        return g.pk

    def serializer(self):
        return {
            'name': self.group_name, 'id': self.pk
        }

    @staticmethod
    def get_all_group(account):
        list_of_group = Group.objects.all()
        choosen = []
        for l in list_of_group:
            if account in l.members:
                choosen.append(l)
        return [i.serializer() for i in choosen]


# class GroupMember(models.Model):
#     group = models.ForeignKey(Group, models.CASCADE)
#     account = models.ForeignKey(Account, models.CASCADE)
#
#     @classmethod
#     def add_member(cls, group, account):
#         gm = GroupMember(group=group, account=account)
#         gm.save()


class GroupForm(forms.Form):
    group_name = forms.CharField(label='Group name', max_length=100)

# class InvitationRequest(models.Model):
#     source_account = models.ForeignKey(Account, on_delete=models.CASCADE)
#     invited_account = models.ForeignKey(Account, on_delete=models.CASCADE)
