from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import TemplateView
from django.contrib.sessions import *
from django.db.models import Q


from IfBoxHp.models import *
from IfBoxHp.forms import *
import re
import math

from datetime import date,datetime,timedelta
import calendar
from pytz import timezone
def checklogin(request):
    flag=False
    if not "username" in request.session:
        if "p" in request.GET:
            nextpage=request.GET["p"]
            request.session["page"]=nextpage
        flag=True
    return flag

def getcontext(request,url):
    url+="?"
    for j,i in enumerate(request.GET):
        param=request.GET[i]
        if j==0:
            url+=i+"="+param
        else:
            url += "&" + i + "=" + param
    return url

def makedatetime(s):
    return ("2000-01-01 "+s)
def makedobject(t):
    h=t.hour
    m=t.minute
    return datetime(2020,1,1,h,m)

def calctimedelta(s,e):
    flag=True
    x=list(map(int,s.split(":")))
    y=list(map(int,e.split(":")))
    start=datetime(2020,1,1,x[0],x[1])
    end=datetime(2020,1,1,y[0],y[1])
    if start>end:
        flag=False
    return flag

def secondstostr(second):
    ss=""
    second=int(second)
    h,m=divmod(second,3600)
    m//=60
    h=str(h)
    m=str(m)
    if len(m)==1:
        m="0"+m
    return h+":"+m


# Create your views here.


# 管理者ログインチェック
def AdminLoginCheck(request):
    flag=False
    if "AdminUser" in request.session:
       flag=True
    return flag


# 管理画面
class AdminView(TemplateView):
    template_name = "KintaiFiles/KintaiAdmin.html"
    def get(self, request, *args, **kwargs):
        context=super(AdminView,self).get_context_data(**kwargs)
        #
        # AdminInformation.objects.create(adminid="admin", adminpass1="abc303")

        if not AdminLoginCheck(request):
            return render(self.request,"KintaiFiles/KintaiAdminLogin.html",context)

        return render(self.request,self.template_name,context)

    def post(self, request, *args, **kwargs):
        ID=request.POST["ID"]
        pass1=request.POST["pass1"]
        llst=AdminInformation.objects.filter(adminid=ID,adminpass1=pass1)
        if len(llst)==0:
            context = super(AdminView, self).get_context_data(**kwargs)
            context["errormessage"]="IDまたはパスワードのいずれかが間違っています"
            return render(self.request,"KintaiFiles/KintaiAdminLogin.html",context)
        else:
            name=llst[0].adminname
            request.session["AdminUser"]=name
            response=redirect("/administrator")
            return response






# 従業員別勤怠入力画面
class KintaiView(TemplateView):
    template_name = "KintaiFiles/Kintai.html"
    def get(self, request, *args, **kwargs):
        context=super(KintaiView,self).get_context_data(**kwargs)
        if not EmpLoginCheck(request):
            return redirect("/emplogin")
        userid=request.session["empuserid"]
        user=EmployeeInfo.objects.filter(primkey=userid)[0]
        if user.jobstatus:
            lastrun=RunningInfo.objects.filter(employeeofrun=EmployeeInfo(primkey=userid))
            if len(lastrun)==0:
                EmployeeInfo.objects.filter(primkey=userid).update(jobstatus=False)
                genba = GenbaInfo.objects.filter(nowrunning=True)
                context["genba"] = genba
                context["empuser"] = EmployeeInfo.objects.filter(primkey=userid)[0]
                return render(self.request, self.template_name, context)
            if lastrun.last().leavetime!=None :
                EmployeeInfo.objects.filter(primkey=userid).update(jobstatus=False)
                genba = GenbaInfo.objects.filter(nowrunning=True)
                context["genba"] = genba
                context["empuser"] = EmployeeInfo.objects.filter(primkey=userid)[0]
                return render(self.request, self.template_name, context)
            lastrun=lastrun.last()
            userstime=lastrun.attendancetime
            starttime=lastrun.genbainfo.start
            endtime=lastrun.genbainfo.end
            workingtime=endtime-starttime
            calcus=makedobject(userstime)
            calcgs=makedobject(starttime)
            if calcus!=calcgs:
                userstime-=calcus-calcgs

            userendtime=userstime+workingtime

            if (userendtime+timedelta(0,10))<(datetime.now())and (lastrun.attendancetime+timedelta(0,10))<datetime.now():
                lastprim=lastrun.primkey
                RunningInfo.objects.filter(primkey=lastprim).update(leavetime=userendtime)
                EmployeeInfo.objects.filter(primkey=userid).update(lastgenba=lastrun.genbainfo.primkey,jobstatus=False)
                context["message"]=str(lastrun.attendancetime.day)+"日の"+lastrun.genbainfo.genbaname+"の現場において退勤打刻の押し忘れがありました。自動で定時退勤にしています。\n退勤時刻を修正する場合は出勤状況確認から該当日時の修正をしてください。"
                genba = GenbaInfo.objects.filter(nowrunning=True)
                context["genba"] = genba
            else:
                context["site"]=GenbaInfo.objects.filter(primkey=user.lastgenba)[0].genbaname
        else:
            genba=GenbaInfo.objects.filter(nowrunning=True)
            context["genba"]=genba
        nowtime=datetime.now()
        m = nowtime.minute
        nowtime -= timedelta(0, m % 15 * 60)
        m=str(nowtime.minute)
        if len(m)==1:
            m="0"+m
        nowtime=str(nowtime.hour)+":"+m
        context["empuser"]=EmployeeInfo.objects.filter(primkey=userid)[0]
        context["nowtime"]=nowtime
        return render(self.request,self.template_name,context)


    def post(self,request,*args,**kwargs):
        if not EmpLoginCheck(request):
            return redirect("/emplogin")
        userid=request.session["empuserid"]
        status=request.POST["status"]
        if status=="sk":
            genbaid=request.POST["genbaid"]
            nowtime=datetime.now()
            print(nowtime)
            genbainfo=GenbaInfo.objects.filter(primkey=genbaid)[0]
            starttime=genbainfo.start
            x=starttime.astimezone()
            print(x.hour)
            sg=makedobject(starttime).astimezone()
            su=makedobject(nowtime).astimezone()
            print(sg,su,"タオ")
            if sg>su:
                nowtime+=(sg-su)

            else:
                m=nowtime.minute
                if m%15!=0:
                    x=15-m%15
                    nowtime+=timedelta(0,x*60)
                print(nowtime)
                nowtime=datetime(nowtime.year,nowtime.month,nowtime.day,nowtime.hour,nowtime.minute)

            RunningInfo.objects.create(employeeofrun=EmployeeInfo(primkey=userid),genbainfo=GenbaInfo(primkey=genbaid),attendancetime=nowtime)
            EmployeeInfo.objects.filter(primkey=userid).update(jobstatus=True,lastgenba=genbaid)
        else:
            lastrun=RunningInfo.objects.filter(employeeofrun=EmployeeInfo(primkey=userid)).last()
            nowtime=datetime.now()
            m=nowtime.minute
            nowtime-=timedelta(0,m%15*60)
            nowtime = datetime(nowtime.year, nowtime.month, nowtime.day, nowtime.hour, nowtime.minute)
            lastprim=lastrun.primkey
            lastgenbaid=lastrun.genbainfo.primkey
            lgenbainfo=GenbaInfo.objects.filter(primkey=lastgenbaid).first()
            ltime=lgenbainfo.end
            lthour=ltime.hour
            ltminute=ltime.minute
            teijitime=datetime(nowtime.year,nowtime.month,nowtime.day,lthour,ltminute)
            if request.POST["dakokutype"]=="teiji":
                nowtime=teijitime
            zangyo=0
            if teijitime<nowtime:
                zangyo=(nowtime-teijitime).seconds

            zangyostr=secondstostr(zangyo)
            RunningInfo.objects.filter(primkey=lastprim).update(leavetime=nowtime,zangyotime=zangyo,zangyostr=zangyostr)
            EmployeeInfo.objects.filter(primkey=userid).update(jobstatus=False)

        return redirect("/kintai")


# 従業員ログインチェック
def EmpLoginCheck(request):
    flag=False
    if "empuserid" in request.session:
        flag=True
    return flag

# 従業員ログイン
class EmployeeLogin(TemplateView):
    template_name = "Employee/EmpLogin.html"
    def get(self, request, *args, **kwargs):
        context=super(EmployeeLogin,self).get_context_data(**kwargs)
        if EmpLoginCheck(request):
            return redirect("/empshift")
        return render(self.request,self.template_name,context)
    def post(self,request,*args,**kwargs):
        context = super(EmployeeLogin, self).get_context_data(**kwargs)
        id       = request.POST["loginid"]
        password = request.POST["password"]
        emp=Employee.objects.filter(loginid=id,password=password)
        if len(emp)==0:
            context["message"]="IDかパスワードが違います。"
            return render(self.request,self.template_name,context)
        emp=emp[0]
        request.session["empuserid"]=emp.primkey
        request.session["empusername"]=emp.name
        return redirect("/empshift")

# 従業員ログアウト
class EmployeeLogOut(TemplateView):
    template_name = "Employee/EmpLogin.html"
    def get(self, request, *args, **kwargs):
        request.session.clear()
        return redirect("/emplogin")
class Employees(TemplateView):
    template_name = "Employee/EmpCalendar.html"
    def get(self, request, *args, **kwargs):
        context=super(Employees,self).get_context_data(**kwargs)
        Employee.objects.create(name="田中",loginid="aaaa",password="1234")
        if not EmpLoginCheck(request):
            return redirect("/emplogin")
        userid=request.session["empuserid"]
        userinfo=Employee.objects.filter(primkey=userid)[0]
        added=userinfo.addday
        added=added.split(",")
        added=added[:len(added)-1]
        added=list(map(int,added))
        now=datetime.now()
        year=now.year
        month=now.month
        today=now.day
        mrange=calendar.monthrange(year,month)
        lastday=mrange[1]
        firstday=datetime(year,10,1).weekday()
        leng=lastday+firstday
        loop=math.ceil(leng/7)
        llst=[]
        for i in range(loop):
            x=[]
            for j in range(7):
                y={}
                num=i*7+j
                if num<firstday or num-firstday+1>lastday:
                    y["exist"]=False
                    y["value"]="　"
                else:
                    day=num-firstday+1
                    y["exist"]=True
                    strnum=str(day)
                    y["value"]=strnum
                    if day<today:
                        y["before"]=True
                    else:
                        y["before"]=False
                        if day in added:
                            y["added"]=True
                        else:
                            y["added"]=False
                x.append(y)
            llst.append(x)
        context["allday"]=llst
        context["lastday"]=lastday

        return render(self.request,self.template_name,context)

    def post(self,request,*args,**kwargs):
        context=super(Employees,self).get_context_data(**kwargs)
        lastday=int(request.POST["lastday"])
        days=[]
        for i in range(1,lastday-1):
            x=int(request.POST["day"+str(i)])
            if x==1:
                days.append(i)
        context["days"]=days
        context["beforeh"]=[k for k in range(11,17)]
        context["afterh"]=[k for k in range(17,24)]

        return render(self.request,"Employee/ShiftEdit.html",context)

# class ShiftEdit(TemplateView):
#     template_name = "Employee/ShiftEdit.html"
#
#     def get(self, request, *args, **kwargs):
#         context = super(ShiftEdit, self).get_context_data(**kwargs)

