from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import TemplateView
from django.contrib.sessions import *
from django.db.models import Q


from IfBoxHp.models import *
from IfBoxHp.forms import *
import re

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

# 本日稼働中情報管理
class AdminAttendance(TemplateView):
    template_name = "KintaiFiles/AdminShutuTaikin.html"
    def get(self, request, *args, **kwargs):
        context=super(AdminAttendance,self).get_context_data(**kwargs)
        if not AdminLoginCheck(request):
            return render(self.request,"KintaiFiles/KintaiAdminLogin.html",context)

        todayat=RunningInfo.objects.filter(attendancetime__date=date.today())
        context["todayat"]=todayat

        return render(self.request,self.template_name,context)

# 従業員情報管理
class AdminEmployee(TemplateView):
    template_name = "KintaiFiles/AdminEmployee.html"
    def get(self, request, *args, **kwargs):
        context=super(AdminEmployee,self).get_context_data(**kwargs)
        if not AdminLoginCheck(request):
            return render(self.request,"KintaiFiles/KintaiAdminLogin.html",context)

        employees=EmployeeInfo.objects.filter(loginaccess=True)

        context["employee"]=employees

        return render(self.request,self.template_name,context)

# 従業員新規追加
class NewEmployee(TemplateView):
    template_name = "KintaiFiles/NewEmployee.html"
    def get(self, request, *args, **kwargs):
        context=super(NewEmployee,self).get_context_data(**kwargs)
        if not AdminLoginCheck(request):
            return render(self.request,"KintaiFiles/KintaiAdminLogin.html",context)

        return render(self.request,self.template_name,context)
    def post(self, request, *args, **kwargs):
        context = super(NewEmployee, self).get_context_data(**kwargs)
        ename=request.POST["ename"]
        loginid=request.POST["loginid"]
        llst=EmployeeInfo.objects.filter(employeename=ename)
        llst2=EmployeeInfo.objects.filter(loginid=loginid)

        # if len(llst)>=1:
        #     context["message"]="従業員名は既に登録されています、別の名前を登録してください"
        #     return render(self.request,self.template_name,context)
        if len(ename)==0:
            context["message"]="名前を入力してください"
            return render(self.request,self.template_name,context)
        if len(loginid)<=3:
            context["message"]="ログインIDは4文字以上で設定してください"
            return render(self.request,self.template_name,context)
        if len(llst2)>=1:
            context["message"]="そのログインIDは既に"+llst2[0].employeename+"さんに使用されています、別のIDを使用してください"
            return render(self.request,self.template_name,context)
        else:
            # パスワード作成
            import random
            passlen=random.randint(7,13)
            moji="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
            mojilen=len(moji)
            newpass=""
            for i in range(passlen):
                newpass+=moji[random.randint(0,mojilen-1)]
            EmployeeInfo.objects.create(employeename=ename,loginid=loginid,loginidpass=newpass)
            id=EmployeeInfo.objects.filter(loginid=loginid,loginidpass=newpass)[0].primkey
            context["id"]=id
            context["registok"]=1
            context["password"]=newpass
            context["loginid"]=loginid
            context["ename"]=ename
            return render(self.request,self.template_name,context)

# 従業員情報編集
class EmployeeEdit(TemplateView):
    template_name = "KintaiFiles/AdminEmployeeEdit.html"
    def get(self, request, *args, **kwargs):
        context=super(EmployeeEdit,self).get_context_data(**kwargs)
        if not AdminLoginCheck(request):
            return render(self.request,"KintaiFiles/KintaiAdminLogin.html",context)
        id=request.GET["id"]
        empuser=EmployeeInfo.objects.filter(primkey=id)[0]
        context["euser"]=empuser
        return render(self.request,self.template_name,context)

    def post(self, request, *args, **kwargs):
        context = super(EmployeeEdit, self).get_context_data(**kwargs)
        prim=request.POST["prim"]
        name=request.POST["name"]
        loginid=request.POST["loginid"]
        password=request.POST["pass"]
        empuser=EmployeeInfo.objects.filter(primkey=prim)[0]
        context["euser"]=empuser
        if len(name)==0:
            context["message"]="名前を空白にすることはできません"
            return render(self.request,self.template_name,context)
        if len(password)<=5:
            context["message"]="パスワードは6文字以上で設定してください"
            return render(self.request,self.template_name,context)
        if len(loginid)<4:
            context["message"]="ログインIDは4文字以上で設定してください"
            return render(self.request,self.template_name,context)
        x=EmployeeInfo.objects.filter(loginid=loginid).exclude(primkey=prim)
        y=EmployeeInfo.objects.filter(employeename=name).exclude(primkey=prim)
        if len(x)>0:
            context["message"]="そのログインIDは既に使用されています。別の物を使用して下さい"
            return render(self.request,self.template_name,context)
        # if len(y)>0:
        #     context["message"]="その名前は既に使われています。別の名前にしてください"
        #     return render(self.request,self.template_name,context)
        EmployeeInfo.objects.filter(primkey=prim).update(employeename=name,loginid=loginid,loginidpass=password)
        return redirect("/employee")

# 従業員の今月出勤情報
class EmployeeShukkin(TemplateView):
    template_name = "KintaiFiles/EmployeeShukkin.html"
    def get(self, request, *args, **kwargs):
        context=super(EmployeeShukkin,self).get_context_data(**kwargs)
        if not AdminLoginCheck(request):
            return render(self.request,"KintaiFiles/KintaiAdminLogin.html",context)
        id=request.GET["id"]
        emprun=RunningInfo.objects.filter(attendancetime__year=date.today().year,attendancetime__month=date.today().month,employeeofrun=id).order_by("attendancetime")
        context["emprun"]=emprun
        context["nissu"]=len(emprun)
        context["name"]=EmployeeInfo.objects.filter(primkey=id)[0].employeename
        return render(self.request,self.template_name,context)

# お客様管理画面
class AdminCustomer(TemplateView):
    template_name = "KintaiFiles/AdminCustomer.html"
    def get(self, request, *args, **kwargs):
        context=super(AdminCustomer,self).get_context_data(**kwargs)
        if not AdminLoginCheck(request):
            return render(self.request,"KintaiFiles/KintaiAdminLogin.html",context)

        customers=CustomerInfo.objects.filter(nowrunning=True)
        for i in customers:
            print(i)
        context["customers"]=customers

        return render(self.request,self.template_name,context)

# お客様新規登録
class NewCustomer(TemplateView):
    template_name = "KintaiFiles/NewCustomer.html"
    def get(self, request, *args, **kwargs):
        context=super(NewCustomer,self).get_context_data(**kwargs)
        if not AdminLoginCheck(request):
            return render(self.request,"KintaiFiles/KintaiAdminLogin.html",context)
        if "lastpage" in request.GET:
            request.session["lastpage"]=request.GET["lastpage"]
        return render(self.request,self.template_name,context)

    def post(self, request, *args, **kwargs):
        context = super(NewCustomer, self).get_context_data(**kwargs)
        cusname=request.POST["customername"]
        llst=CustomerInfo.objects.filter(compname=cusname)

        if len(llst)>=1:
            context["message"]="お客様名は既に登録されています"
            return render(self.request,self.template_name,context)
        if len(cusname)<=2:
            context["message"]="会社名称は3文字以上で登録してください"
            return render(self.request,self.template_name,context)
        else:
            CustomerInfo.objects.create(compname=cusname)
            if "lastpage" in request.session:
                if request.session["lastpage"]=="genba":
                    return redirect("/sinkigenba")
            return redirect("/customer")

# お客様名編集
class EditCustomer(TemplateView):
    template_name = "KintaiFiles/EditCustomer.html"
    def get(self, request, *args, **kwargs):
        context=super(EditCustomer,self).get_context_data(**kwargs)
        if not AdminLoginCheck(request):
            return render(self.request,"KintaiFiles/KintaiAdminLogin.html",context)
        id=request.GET["id"]
        context["customer"]=CustomerInfo.objects.filter(primkey=id)[0]
        return render(self.request,self.template_name,context)
    def post(self, request, *args, **kwargs):
        id=request.POST["id"]
        name=request.POST["name"]
        CustomerInfo.objects.filter(primkey=id).update(compname=name)
        return redirect("/customer")

# お客様別現場一覧
class GenbaOfCustomer(TemplateView):
    template_name = "KintaiFiles/GenbaOfCustomer.html"
    def get(self, request, *args, **kwargs):
        context=super(GenbaOfCustomer,self).get_context_data(**kwargs)
        if not AdminLoginCheck(request):
            return render(self.request,"KintaiFiles/KintaiAdminLogin.html",context)
        customerid=int(request.GET["cid"])
        customername=CustomerInfo.objects.filter(primkey=customerid)[0].compname
        today=date.today()
        year=today.year
        month=today.month
        # rgenba=RunningInfo.objects.filter(attendancetime__year=year,attendancetime__month=month,genbainfo=GenbaInfo(compofgenba=CustomerInfo(primkey=customerid)))
        rgenba=RunningInfo.objects.filter(attendancetime__year=year,attendancetime__month=month)
        t=[k.genbainfo.compofgenba.primkey for k in rgenba]
        rgenba2=[]
        for j,i in enumerate(t):
            if i==customerid:
                rgenba2.append(rgenba[j])
        runprims=[k.genbainfo.primkey for k in rgenba2]
        runprims=list(set(runprims))
        rungenba=[]
        for i in runprims:
            x={}
            genba=GenbaInfo.objects.filter(primkey=i)[0]
            x["id"]=genba.primkey
            x["name"]=genba.genbaname
            rungenba.append(x)
        if len(rungenba)==0:
            context["message"]=customername+"様の今月稼働中の現場は0件です。"
        context["cname"]=customername
        context["rgenba"]=rungenba
        return render(self.request,self.template_name,context)


class AdminGenba(TemplateView):
    template_name = "KintaiFiles/AdminGenba.html"
    def get(self, request, *args, **kwargs):
        context=super(AdminGenba,self).get_context_data(**kwargs)
        if not AdminLoginCheck(request):
            return render(self.request,"KintaiFiles/KintaiAdminLogin.html",context)

        today=date.today()
        year=today.year
        month=today.month

        runninggenba=RunningInfo.objects.filter(attendancetime__year=year,attendancetime__month=month).order_by("genbainfo")
        runninggenba=[k.genbainfo.primkey for k in runninggenba]
        genba=GenbaInfo.objects.all()
        runninggenba=[{"id":k.primkey,"name":k.genbaname} for k in genba if k.primkey in runninggenba]
        print(runninggenba)
        context["runninggenba"]=runninggenba
        return render(self.request,self.template_name,context)



# 稼働中の現場情報管理
class GenbaKanri(TemplateView):
    template_name = "KintaiFiles/KadouGenbaKanri.html"

    def get(self, request, *args, **kwargs):
        context = super(GenbaKanri, self).get_context_data(**kwargs)
        if not AdminLoginCheck(request):
            return render(self.request, "KintaiFiles/KintaiAdminLogin.html", context)

        genba = GenbaInfo.objects.filter(nowrunning=True)
        context["genba"] = genba
        return render(self.request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = super(GenbaKanri, self).get_context_data(**kwargs)
        genbaid=request.POST["genbaid"]
        stime=request.POST["stime"+str(genbaid)]
        ttime=request.POST["ttime"+str(genbaid)]
        if stime=="" or ttime=="":
            context["message"]="出勤時刻と退勤時刻は両方入力してください"
            genba = GenbaInfo.objects.filter(nowrunning=True)
            context["genba"] = genba
            return render(self.request, self.template_name, context)
        if not calctimedelta(stime,ttime):
            context["message"]="退勤時刻が出勤時刻よりも前になっています"
            genba = GenbaInfo.objects.filter(nowrunning=True)
            context["genba"] = genba
            return render(self.request, self.template_name, context)
        x=list(map(int,stime.split(":")))
        y=list(map(int,ttime.split(":")))
        stime=datetime(2020,1,1,x[0],x[1])
        ttime=datetime(2020,1,1,y[0],y[1])

        GenbaInfo.objects.filter(primkey=genbaid).update(start=stime,end=ttime)

        return redirect("/genbakanri")



# 現場別稼働状況
class GenbaBetu(TemplateView):
    template_name = "KintaiFiles/GenbaBetuKado.html"

    def get(self, request, *args, **kwargs):
        context = super(GenbaBetu, self).get_context_data(**kwargs)
        if not AdminLoginCheck(request):
            return render(self.request, "KintaiFiles/KintaiAdminLogin.html", context)
        id=request.GET["id"]
        context["genbaname"]=GenbaInfo.objects.filter(primkey=id)[0].genbaname
        kado=[]
        year=date.today().year
        month=date.today().month
        lastdate=calendar.monthrange(year,month)[1]
        genbainfo=GenbaInfo.objects.filter(primkey=id)[0]
        e=genbainfo.end.astimezone()
        print(e.hour)
        hour=e.hour
        minute=e.minute
        sums=0
        for day in range(1,lastdate+1):
            today=datetime(year,month,day,hour,minute).astimezone(timezone('Asia/Tokyo'))
            x={"day":day}
            d = RunningInfo.objects.filter(attendancetime__year=year,attendancetime__month=month,attendancetime__day=day,genbainfo=id)

            # sumzangyo=sum([(k.leavetime.astimezone()-today).seconds for k in d if k.leavetime.astimezone(timezone('Asia/Tokyo'))>today])

            leng=len(d)
            sums+=leng
            x["ninku"]=leng
            names=",".join([k.employeeofrun.employeename for k in d])
            x["names"]=names
            if leng!=0:
                x["id"]=id
            zangyo=[k.zangyotime if k.zangyotime!=None else 0.0 for k in d ]
            szangyo=sum(zangyo)
            if szangyo!=0:
                szangyo=secondstostr(szangyo)
                x["sumzangyo"]=szangyo
            kado.append(x)

        context["kado"] = kado
        context["kadoninku"]=sums
        context["year"]=year
        context["month"]=month
        return render(self.request, self.template_name, context)

#現場新規登録
class NewGenba(TemplateView):
    template_name = "KintaiFiles/NewGenba.html"
    def get(self, request, *args, **kwargs):
        context = super(NewGenba, self).get_context_data(**kwargs)
        if not AdminLoginCheck(request):
            return render(self.request, "KintaiFiles/KintaiAdminLogin.html", context)
        companies=CustomerInfo.objects.filter(nowrunning=True)
        context["companies"]=companies
        return render(self.request, self.template_name, context)
    def post(self, request, *args, **kwargs):
        context = super(NewGenba, self).get_context_data(**kwargs)
        genbaname=request.POST["genbaname"]
        compid=request.POST["compid"]
        stime=request.POST["stime"]
        ttime=request.POST["ttime"]
        if compid=="none":
            llst = GenbaInfo.objects.filter(genbaname=genbaname)
        else:
            llst=GenbaInfo.objects.filter(genbaname=genbaname,compofgenba=CustomerInfo(primkey=compid))
        companies=CustomerInfo.objects.filter(nowrunning=True)
        context["companies"]=companies

        if stime=="" or ttime=="":
            context["message"]="出勤時刻と退勤時刻は両方入力してください"
            return render(self.request, self.template_name, context)
        if not calctimedelta(stime,ttime):
            context["message"]="退勤時刻が出勤時刻よりも前になっています"
            return render(self.request, self.template_name, context)

        if len(llst)>=1:
            context["message"]="現場は既に登録されています"
            return render(self.request,self.template_name,context)
        if len(genbaname)<=1:
            context["message"]="現場名称は2文字以上で登録してください"
            return render(self.request,self.template_name,context)
        else:
            start=makedatetime(stime)
            end=makedatetime(ttime)
            if compid=="none":
                GenbaInfo.objects.create(genbaname=genbaname,start=start,end=end)
            else:
                GenbaInfo.objects.create(genbaname=genbaname,start=start,end=end,compofgenba=CustomerInfo(primkey=compid))
            context["message"]="現場名:"+genbaname+"を新規に追加しました"
            return redirect("/genbakanri")

# 現場詳細
class GenbaShosai(TemplateView):
    template_name = "KintaiFiles/AdminGenbaShosai.html"
    def get(self, request, *args, **kwargs):
        context = super(GenbaShosai, self).get_context_data(**kwargs)
        if not AdminLoginCheck(request):
            return render(self.request, "KintaiFiles/KintaiAdminLogin.html", context)
        year=request.GET["year"]
        month=request.GET["month"]
        day=request.GET["day"]
        id=request.GET["id"]
        runinfo=RunningInfo.objects.filter(genbainfo=id,attendancetime__year=year,attendancetime__month=month,attendancetime__day=day)
        genba=GenbaInfo.objects.filter(primkey=id)
        context["runinfo"]=runinfo
        context["genba"]=genba[0].genbaname
        context["day"]=day
        context["genbaid"]=genba[0].primkey
        return render(self.request, self.template_name, context)

# 過去の現場
class PastGenba(TemplateView):
    template_name = "KintaiFiles/PastGenba.html"
    def get(self, request, *args, **kwargs):
        context = super(PastGenba, self).get_context_data(**kwargs)
        if not AdminLoginCheck(request):
            return render(self.request, "KintaiFiles/KintaiAdminLogin.html", context)
        genba = GenbaInfo.objects.filter(nowrunning=False)
        context["genba"]=genba
        return render(self.request, self.template_name, context)

class AdminEdit(TemplateView):
    template_name = "KintaiFiles/AdminKanri.html"
    def get(self, request, *args, **kwargs):
        context=super(AdminEdit,self).get_context_data(**kwargs)
        if not AdminLoginCheck(request):
            return render(self.request,"KintaiFiles/KintaiAdminLogin.html",context)
        context["admin"]=AdminInformation.objects.filter(primkey=1)[0]

        return render(self.request,self.template_name,context)


# 情報の追加など
class InfoChange(TemplateView):
    template_name = "KintaiFiles/KadouGenbaKanri.html"

    def get(self, request, *args, **kwargs):
        context = super(InfoChange, self).get_context_data(**kwargs)
        if not AdminLoginCheck(request):
            return render(self.request, "KintaiFiles/KintaiAdminLogin.html", context)

        action=request.GET["action"]
        if action=="logout":
            request.session.clear()
            return redirect("/administrator")
        id=request.GET["id"]

        if action=="delete":
            GenbaInfo.objects.filter(primkey=id).update(nowrunning=False)
            context["message"] = "稼働中の現場から外しました"
            return redirect("/genbakanri")

        elif action=="run":
            GenbaInfo.objects.filter(primkey=id).update(nowrunning=True)
            return redirect("/pastgenba")

        elif action=="delemployee":
            id = request.GET["id"]
            EmployeeInfo.objects.filter(primkey=id).update(loginaccess=False)
            return redirect("/employee")

        elif action=="delcustomer":
            id = request.GET["id"]
            CustomerInfo.objects.filter(primkey=id).update(nowrunning=False)
            return redirect("/customer")

    def post(self,request,*args,**kwargs):
        context=super(InfoChange,self).get_context_data(**kwargs)
        action=request.POST["action"]
        context["admin"] = AdminInformation.objects.filter(primkey=1)[0]
        if action=="admininfochange":
            loginid=request.POST["id"]
            loginpas=request.POST["pass1"]
            loginpas2=request.POST["pass2"]
            if not(len(loginid)>=4 and len(loginpas)>=6):
                context["message"]="IDは4文字以上、パスワードは6文字以上で設定してください"
                return render(self.request,"KintaiFiles/AdminKanri.html",context)
            if not loginpas==loginpas2:
                context["message"]="パスワードが一致しません"
                return render(self.request,"KintaiFiles/AdminKanri.html",context)
            AdminInformation.objects.filter(primkey=1).update(adminid=loginid,adminpass1=loginpas)
            return redirect("/admininfo")
        if action=="usepass":
            use=int(request.POST["uselogin"])
            flag=True if use==1 else False
            AdminInformation.objects.filter(primkey=1).update(uselogin=flag)
            return redirect("/admininfo")


# 従業員ログインチェック
def EmpLoginCheck(request):
    flag=False
    if "empuserid" in request.session:
        flag=True
    return flag


# 勤怠ログイン画面
class KintaiLogin(TemplateView):
    template_name = "KintaiFiles/KintaiLogin.html"
    def get(self, request, *args, **kwargs):
        if EmpLoginCheck(request):
            return redirect("/kintai")
        context=super(KintaiLogin,self).get_context_data(**kwargs)
        usepass=AdminInformation.objects.filter(primkey=1)[0].uselogin
        context["usepass"]=usepass
        return render(self.request,self.template_name,context)
    def post(self,request,*args,**kwargs):
        context=super(KintaiLogin,self).get_context_data(**kwargs)
        usepass=AdminInformation.objects.filter(primkey=1)[0].uselogin
        context["usepass"]=usepass
        if usepass:
            loginid=request.POST["id"]
            loginpas=request.POST["password"]
            user=EmployeeInfo.objects.filter(loginid=loginid,loginidpass=loginpas,loginaccess=True)
            if len(user)==0:
                context["message"]="IDまたはパスワードが違います"
                return render(self.request,self.template_name,context)
        else:
            loginid=request.POST["id"]
            user=EmployeeInfo.objects.filter(loginid=loginid,loginaccess=True)
            if len(user)==0:
                context["message"]="IDが違います"
                return render(self.request,self.template_name,context)
        user=user[0]
        request.session["empuserid"]=user.primkey
        request.session["username"]=user.employeename
        return redirect("/kintai")



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

# 従業員別パスワード編集
class EmployeePassEdit(TemplateView):
    template_name = "KintaiFiles/EmpPassEdit.html"
    def get(self, request, *args, **kwargs):
        context=super(EmployeePassEdit,self).get_context_data(**kwargs)
        if not EmpLoginCheck(request):
            return redirect("/emplogin")
        userid=request.session["empuserid"]
        user=EmployeeInfo.objects.filter(primkey=userid)[0]
        context["empuser"]=user
        return render(self.request,self.template_name,context)
    def post(self,request,*args,**kwargs):
        context=super(EmployeePassEdit,self).get_context_data(**kwargs)
        userid=request.session["empuserid"]
        user=EmployeeInfo.objects.filter(primkey=userid)[0]
        context["empuser"]=user
        pass1=request.POST["pass1"]
        pass2=request.POST["pass2"]
        if pass1!=pass2:
            context["message"]="パスワードが一致しません"
            return render(self.request,self.template_name,context)
        if len(pass1)<6:
            context["message"]="パスワードは6文字以上で入力してください"
            return render(self.request,self.template_name,context)
        EmployeeInfo.objects.filter(primkey=userid).update(loginidpass=pass1)
        return redirect("/kintai")

# 従業員出勤情報
class EmployeeThisMonth(TemplateView):
    template_name = "KintaiFiles/EmpThisMonth.html"
    def get(self, request, *args, **kwargs):
        context=super(EmployeeThisMonth,self).get_context_data(**kwargs)
        if not EmpLoginCheck(request):
            return redirect("/emplogin")
        userid=request.session["empuserid"]
        user=EmployeeInfo.objects.filter(primkey=userid)[0]
        context["empuser"]=user
        year=date.today().year
        month=date.today().month
        context["month"]=month
        emprun=RunningInfo.objects.filter(attendancetime__year=year,attendancetime__month=month,employeeofrun=userid).order_by("genbainfo")
        context["emprun"]=emprun
        return render(self.request,self.template_name,context)

class ChangeInfoEmp(TemplateView):
    def get(self, request, *args, **kwargs):
        context=super(ChangeInfoEmp,self).get_context_data(**kwargs)
        if not EmpLoginCheck(request):
            return redirect("/emplogin")

        userid=request.session["empuserid"]
        action=request.GET["action"]

        if action=="delshukkin":
            id = request.GET["id"]
            RunningInfo.objects.filter(primkey=id).delete()
            return redirect("/empthismonth")
        if action=="logout":
            request.session.clear()
            return redirect("/kintai")



    def post(self,request,*args,**kwargs):
        context=super(ChangeInfoEmp,self).get_context_data(**kwargs)
        if not EmpLoginCheck(request):
            return redirect("/emplogin")
        userid=request.session["empuserid"]
        context["empuser"]=EmployeeInfo.objects.filter(primkey=userid)[0]
        id=request.POST["id"]
        p = RunningInfo.objects.filter(primkey=id).first()
        t = request.POST["ltime" + str(id)]
        if t == "":
            year = date.today().year
            month = date.today().month
            context["message"] = "時間を入力してください"
            emprun = RunningInfo.objects.filter(attendancetime__year=year, attendancetime__month=month,
                                                employeeofrun=userid).order_by("attendancetime")
            context["emprun"] = emprun
            return render(self.request, "KintaiFiles/EmpThisMonth.html", context)
        # 出勤日の年月日を取得
        year = p.attendancetime.year
        month = p.attendancetime.month
        day = p.attendancetime.day
        t = list(map(int, t.split(":")))
        t = datetime(year, month, day, t[0], t[1])
        if t<p.attendancetime:
            context["message"]="退勤時刻が出勤時刻よりも前になっています"
            emprun = RunningInfo.objects.filter(attendancetime__year=year, attendancetime__month=month,
                                                employeeofrun=userid).order_by("attendancetime")
            context["emprun"] = emprun
            return render(self.request, "KintaiFiles/EmpThisMonth.html", context)

        runinfo=RunningInfo.objects.filter(primkey=id).first()


        #  現場の定時終了時刻取得
        lastgenbaid = runinfo.genbainfo.primkey
        lgenbainfo = GenbaInfo.objects.filter(primkey=lastgenbaid).first()
        ltime = lgenbainfo.end
        lthour = ltime.hour
        ltminute = ltime.minute
        # 出勤日の定時終了時刻datetimeインスタンス作成
        teijitime = datetime(year,month,day, lthour, ltminute)
        # 残業時間
        zangyo=0
        if t>teijitime:
            zangyo=(t-teijitime).seconds
        zangyostr=secondstostr(zangyo)
        RunningInfo.objects.filter(primkey=id).update(leavetime=t,zangyotime=zangyo,zangyostr=zangyostr)
        return redirect("/empthismonth")