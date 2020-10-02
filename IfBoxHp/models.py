from django.db import models

# Create your models here.

# 管理者情報(管理画面にログインの際に必要)


# 現場情報
# class GenbaInfo(models.Model):
#     primkey = models.AutoField(primary_key=True)
#     genbaname = models.CharField(max_length=1000)
#     compofgenba = models.ForeignKey("CustomerInfo",on_delete=models.SET_NULL,null=True)
#     nowrunning = models.BooleanField(default=True)
#     start=models.DateTimeField(null=True)
#     end=models.DateTimeField(null=True)

# 従業員情報

class Employee(models.Model):
    primkey = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    loginid=models.CharField(max_length=30)
    password=models.CharField(max_length=30)
    addday=models.CharField(max_length=1000)
    addshift=models.CharField(max_length=1000)
    access=models.BooleanField(default=True)
















