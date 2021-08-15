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


class Address(models.Model):
    address = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=60, default="Tehran")
    state = models.CharField(max_length=30, default="Tehran")
    country = models.CharField(max_length=50, default="Iran")

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Address'


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, default=None)
    phone_number = models.CharField(max_length=17, blank=True)
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
            'uid': self.uid, 'username': self.user.username, 'email': self.user.email, 'credit': self.wallet.credit,
            'phone_number': self.phone_number
        }

    def serializer_2(self):
        return {
            'id': self.user.pk, 'name': self.user.username}

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = Account.generate_uid()

        return super(Account, self).save(*args, **kwargs)

    @classmethod
    def get_account_by_user(cls, user_id):
        return cls.objects.get(user__id=user_id)

    @classmethod
    def new_account(cls, user):
        adr = Address()
        adr.save()
        w = Wallet()
        w.save()
        acc = Account(user=user, wallet=w, address=adr)
        acc.save()

    @staticmethod
    def get_all_accounts():
        l = Account.objects.all()
        return [i.serializer_2() for i in l]


class Expense(models.Model):
    debtor = models.ForeignKey(Account, related_name="debtor", on_delete=models.CASCADE, null=False)
    creditor = models.ForeignKey(Account, related_name="creditor", on_delete=models.CASCADE, null=False)
    amount = models.IntegerField()
    description = models.CharField(max_length=300)

    def serializer(self):
        return {
            'cost': self.amount,
            'description': self.description
        }

    @staticmethod
    def get_all_expenses(debtor):
        l = Expense.objects.filter(debtor=debtor)
        return [i.serializer() for i in l]


class Contact(models.Model):
    account = models.ForeignKey(Account, related_name="contacts", on_delete=models.CASCADE, null=False)
    contact_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=False)

    def serializer(self):
        return {
            'name': self.contact_account.user.username, 'email': self.contact_account.user.email,
            'id': self.contact_account.user.id
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
        list_of_contacts = Contact.objects.filter(account=account)
        return [i.serializer() for i in list_of_contacts]


class EditForm(forms.Form):
    address = forms.CharField(label='address', max_length=100)
    city = forms.CharField(label='city', max_length=60)
    state = forms.CharField(label='state', max_length=30)
    country = forms.CharField(label='country', max_length=50)
    phone_number = forms.CharField(label='phone number', max_length=17)
