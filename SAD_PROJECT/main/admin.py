from django.contrib import admin

from .models import Account, Contact, Transaction, Wallet

admin.site.register(Account)
admin.site.register(Wallet)
admin.site.register(Contact)
admin.site.register(Transaction)
