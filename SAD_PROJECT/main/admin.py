from django.contrib import admin

from .models import Account, Wallet, Contact, Transaction, Expense, Share

admin.site.register(Account)
admin.site.register(Wallet)
admin.site.register(Contact)
admin.site.register(Transaction)
admin.site.register(Expense)
admin.site.register(Share)
