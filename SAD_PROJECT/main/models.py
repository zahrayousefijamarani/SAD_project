import random
import string

from django.contrib.auth.models import User
from django.db import models

ID_FIELD_LENGTH = 16
alphabet = string.ascii_lowercase + string.digits


def random_id(length):
    def byte_to_base32_chr(byte):
        return alphabet[byte & 31]

    random_bytes = [random.randint(0, 0xFF) for i in range(length)]
    return ''.join(map(byte_to_base32_chr, random_bytes))


# Create your models here
class Wallet(models.Model):
    credit = models.DecimalField(null=False, decimal_places=2, max_digits=20, default="0.00")


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

    def serialize(self):
        return str(self.address) + ";" + str(self.city) + ',' + str(self.state) + ',' + str(self.country)


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, default=None)
    phone_number = models.CharField(max_length=17, blank=True)
    wallet = models.ForeignKey(Wallet, related_name='accounts', on_delete=models.CASCADE)
    access_final_date = models.DateField(verbose_name='تاریخ انقضای token', auto_now=True)
    uid = models.CharField(max_length=ID_FIELD_LENGTH, null=False, blank=False, unique=True, verbose_name='آیدی یکتا')
    is_admin = models.BooleanField(default=False)

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
            'phone_number': self.phone_number, 'is_admin': self.is_admin, 'address': self.address.serialize()
        }

    def serializer_2(self):
        return {
            'id': self.user.pk, 'name': self.user.username, 'email': self.user.email, }

    def serializer_3(self):
        return self.user.pk, self.user.username

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


class AccPer(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    percent = models.IntegerField()


class Share(models.Model):
    name = models.CharField(max_length=100, default="share")
    address = models.ForeignKey(Address, on_delete=models.CASCADE, default=None)
    date = models.DateField()
    image = models.ImageField(null=True, blank=True)
    accPers = models.ManyToManyField(AccPer)
    credit = models.DecimalField(null=False, decimal_places=2, max_digits=20, default="0.0")
    group_id = models.IntegerField(default=0)
    creditor = models.ForeignKey(Account, on_delete=models.CASCADE)

    def serializer(self):
        return {
            'date': self.date, 'address': self.address.address, 'id': self.pk, 'name': self.name
        }

    def build_expenses(self):
        for accper in self.accPers.all():
            if self.creditor == accper.account:
                continue
            e = Expense(creditor=self.creditor, share=self, debtor=accper.account, description=self.address)
            e.amount = (self.credit * accper.percent) / 100
            e.save()

    @staticmethod
    def get_share_by_id(id):
        return Share.objects.get(pk=id)

    @staticmethod
    def add_shares(id, account, percent, amount):
        s = Share.get_share_by_id(id)
        if str(amount) != '':
            percent = float((float(amount) / float(s.credit)) * 100)
        a = AccPer(account=account, percent=percent)
        a.save()
        s.accPers.add(a)
        s.save()

    @staticmethod
    def get_shares_for_gp(gp_id):
        a = Share.objects.filter(group_id=gp_id)
        return [i.serializer() for i in a]


class Expense(models.Model):
    debtor = models.ForeignKey(Account, related_name="debtor", on_delete=models.CASCADE, null=False)
    creditor = models.ForeignKey(Account, related_name="creditor", on_delete=models.CASCADE, null=False)
    share = models.ForeignKey(Share, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    description = models.CharField(max_length=300)
    payed = models.BooleanField(default=False)
    payer = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)

    def serializer(self):
        if self.payer:
            return {
                'cost': self.amount,
                'description': self.description,
                'id': self.pk,
                'debtor': self.debtor.user.username,
                'creditor': self.creditor.user.username,
                'payer': self.payer.user.username,
            }

        return {
            'cost': self.amount,
            'description': self.description,
            'id': self.pk,
            'debtor': self.debtor.user.username,
            'creditor': self.creditor.user.username,
            'payer': '',
        }

    @staticmethod
    def pay_expenses(expense_id, payer):
        e = Expense.objects.get(pk=expense_id)
        if e is None:
            return "Expense does not exist."
        if not e.payed:
            e.payed = True
            e.payer = payer
            creditor_wallet = e.creditor.wallet
            payer_wallet = payer.wallet

            payer_wallet.credit -= e.amount
            payer_wallet.save()

            creditor_wallet.credit += e.amount
            creditor_wallet.save()

            e.save()
            return None
        return "Already payed."

    @staticmethod
    def get_all_expenses(debtor):
        l = Expense.objects.filter(debtor=debtor)
        return [i.serializer() for i in l]

    @staticmethod
    def get_payed_debtor_expenses(debtor):
        l = Expense.objects.filter(debtor=debtor, payed=True)
        return [i.serializer() for i in l]

    @staticmethod
    def get_payed_payer_expenses(debtor):
        l = Expense.objects.filter(payer=debtor, payed=True)
        return [i.serializer() for i in l]

    @staticmethod
    def get_not_payed_expenses(debtor):
        l = Expense.objects.filter(debtor=debtor, payed=False)
        return [i.serializer() for i in l]

    @staticmethod
    def get_friend_not_payed_expenses(account):
        contacts = Contact.objects.filter(account=account)
        e = []
        for c in contacts:
            c_e = Expense.get_not_payed_expenses(c.contact_account)
            for ex in c_e:
                e.append(ex)
        return e


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
        c = Contact(account=d, contact_account=s)
        c.save()

    @classmethod
    def get_contacts(cls, account):
        if account is None:
            return []
        list_of_contacts = Contact.objects.filter(account=account)
        return [i.serializer() for i in list_of_contacts]
