from django import forms
from django.db import models
# Create your models here.
from main.models import Account


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
        g.members.add(admin)
        return g.pk

    @staticmethod
    def add_members(id, member_list):
        gp = Group.objects.get(pk=id)
        for l in member_list:
            gp.members.add(l)

    @staticmethod
    def get_group(id):
        return Group.objects.get(pk=id)

    def serializer(self):
        return {
            'name': self.group_name, 'id': self.pk
        }

    @staticmethod
    def get_all_group(account):
        list_of_group = Group.objects.all()
        choosen = []

        for l in list_of_group:
            if account in l.members.all():
                choosen.append(l)
        return [i.serializer() for i in choosen]

    @classmethod
    def get_members(cls, gp, is_3=False):
        l = gp.members.all()
        if not is_3:
            return [i.serializer_2() for i in l]
        return [i.serializer_3() for i in l]


class GroupMember(models.Model):
    group = models.ForeignKey(Group, models.CASCADE)
    account = models.ForeignKey(Account, models.CASCADE)

    @classmethod
    def add_member(cls, group, account):
        gm = GroupMember(group=group, account=account)
        gm.save()


class GroupForm(forms.Form):
    group_name = forms.CharField(label='Group name', max_length=100)
