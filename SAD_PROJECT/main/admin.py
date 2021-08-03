from django.contrib import admin

from .models import Account, Wallet, Contact, Transaction

admin.site.register(Account)
admin.site.register(Wallet)
admin.site.register(Contact)
admin.site.register(Transaction)
