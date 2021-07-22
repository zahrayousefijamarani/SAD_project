from django.db import models


# Create your models here.
class Account(models.Model):
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=30)

    def __str__(self):
        return str(self.username)
