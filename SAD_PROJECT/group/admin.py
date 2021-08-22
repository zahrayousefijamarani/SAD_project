from django.contrib import admin
# Register your models here.
from group.models import Group, GroupMember

admin.site.register(Group)
admin.site.register(GroupMember)
