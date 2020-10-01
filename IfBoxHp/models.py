from django.db import models

# Create your models here.

class Person(models.Model):

    MAN = 0
    WOMAN = 1

    HOKKAIDO = 0
    TOHOKU = 5
    TOKYO = 10
    CHIBA = 11
    KANAGAWA = 12
    SAITAMA = 13
    TOCHIGI = 14
    IBARAGI = 15
    CHUBU = 20
    KANSAI = 25
    CHUGOKU = 30
    SHIKOKU = 35
    KYUSHU = 40
    OKINAWA = 45

    # 名前
    name = models.CharField(max_length=128)

class User(models.Model):
    primkey=models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    logindate=models.DateTimeField(auto_now=True)
    userimg=models.ImageField(upload_to="personimage/",default="no-image.png")

class Diaries(models.Model):
    primkey=models.IntegerField(primary_key=False)
    article = models.CharField(max_length=1000)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)

class UserFriends(models.Model):
    userid=models.IntegerField(primary_key=False)
    friendid=models.ForeignKey(User,on_delete=models.CASCADE)
    created=models.DateTimeField(auto_now_add=True)

class UserMessage(models.Model):
    primkey=models.AutoField(primary_key=True)
    userid=models.ForeignKey("User",on_delete=models.CASCADE,related_name="myuser")
    friendid=models.ForeignKey("User",on_delete=models.CASCADE)
    sended=models.DateTimeField(auto_now_add=True)
    opend=models.BooleanField(default=False)
    sendisme=models.BooleanField(default=True)
    message=models.CharField(max_length=1000,default="")



# 勤怠管理専用ページ

# 管理者情報(管理画面にログインの際に必要)
class AdminInformation(models.Model):
    primkey = models.AutoField(primary_key=True)
    adminid = models.CharField(max_length=1000)
    adminpass1 = models.CharField(max_length=1000)
    adminpass2 = models.CharField(max_length=1000)
    adminname = models.CharField(max_length=1000)
    uselogin=models.BooleanField(default=True)

# お客様情報
class CustomerInfo(models.Model):
    primkey = models.AutoField(primary_key=True)
    compname = models.CharField(max_length=1000)
    nowrunning=models.BooleanField(default=True)

# 現場情報
class GenbaInfo(models.Model):
    primkey = models.AutoField(primary_key=True)
    genbaname = models.CharField(max_length=1000)
    compofgenba = models.ForeignKey("CustomerInfo",on_delete=models.SET_NULL,null=True)
    nowrunning = models.BooleanField(default=True)
    start=models.DateTimeField(null=True)
    end=models.DateTimeField(null=True)

# 従業員情報
class EmployeeInfo(models.Model):
    primkey = models.AutoField(primary_key=True)
    employeename = models.CharField(max_length=1000)
    jobstatus = models.BooleanField(default=False)
    loginid=models.CharField(max_length=100)
    loginidpass=models.CharField(max_length=50)
    lastgenba=models.IntegerField(null=True,primary_key=False)
    loginaccess= models.BooleanField(default=True)


# 稼働状況
class RunningInfo(models.Model):
    primkey = models.AutoField(primary_key=True)
    employeeofrun=models.ForeignKey("EmployeeInfo",on_delete=models.SET_NULL,null=True)
    genbainfo=models.ForeignKey("GenbaInfo",on_delete=models.SET_NULL,null=True)
    attendancetime=models.DateTimeField(null=True)
    leavetime=models.DateTimeField(null=True)
    zangyotime=models.FloatField(null=True,default=0.0)
    zangyostr = models.CharField(max_length=10,default="0:00")



















