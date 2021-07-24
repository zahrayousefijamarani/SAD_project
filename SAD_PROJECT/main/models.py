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
    credit = models.CharField(max_length=10)


class Transaction(models.Model):
    date = models.DateField(auto_now=True)
    description = models.CharField(max_length=100)
    payment_type = models.CharField(max_length=100)
    cash_amount = models.CharField(max_length=10)
    wallet = models.ForeignKey(Wallet, related_name='transactions', on_delete=models.CASCADE)


class Account(models.Model):
    user = models.ForeignKey(User, related_name='accounts', on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, related_name='accounts', on_delete=models.CASCADE)
    access_final_date = models.DateField(verbose_name='تاریخ انقضای token')
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
            'uid': self.uid,
        }

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = Account.generate_uid()

        return super(Account, self).save(*args, **kwargs)
