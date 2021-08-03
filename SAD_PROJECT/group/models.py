from django.db import models

# Create your models here.
from main.models import Account


class Group(models.Model):
    group_name = models.CharField(max_length=250)
    admin = models.ForeignKey(Account, on_delete=models.CASCADE)

    @classmethod
    def create_group(cls, name, admin):
        if name == "" or admin is None:
            return
        g = Group(group_name=name, admin=admin)
        g.save()


class GroupMember(models.Model):
    group = models.ForeignKey(Group, models.CASCADE)
    account = models.ForeignKey(Account, models.CASCADE)

    @classmethod
    def add_member(cls, group, account):
        gm = GroupMember(group=group, account=account)
        gm.save()
