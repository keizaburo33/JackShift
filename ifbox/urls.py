"""ifbox URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import IfBoxHp.views as allview
urlpatterns = [
    path('admin/', admin.site.urls),
    path("kintai", allview.KintaiView.as_view()),
    path("administrator", allview.AdminView.as_view()),
    path("attendancetoday", allview.AdminAttendance.as_view()),
    path("employee", allview.AdminEmployee.as_view()),
    path("customer", allview.AdminCustomer.as_view()),
    path("genba", allview.AdminGenba.as_view()),
    path("genbakanri", allview.GenbaKanri.as_view()),
    path("admininfo", allview.AdminEdit.as_view()),
    path("newcustomer", allview.NewCustomer.as_view()),
    path("sinkigenba", allview.NewGenba.as_view()),
    path("changeinfo", allview.InfoChange.as_view()),
    path("pastgenba", allview.PastGenba.as_view()),
    path("newemployee", allview.NewEmployee.as_view()),
    path("eshukkin", allview.EmployeeShukkin.as_view()),
    path("emplogin", allview.KintaiLogin.as_view()),
    path("empedit", allview.EmployeeEdit.as_view()),
    path("emppassedit", allview.EmployeePassEdit.as_view()),
    path("empthismonth", allview.EmployeeThisMonth.as_view()),
    path("changeinfoemp", allview.ChangeInfoEmp.as_view()),
    path("genbamonthinfo", allview.GenbaBetu.as_view()),
    path("genbashosai", allview.GenbaShosai.as_view()),
    path("gofcustomer", allview.GenbaOfCustomer.as_view()),
    path("customeredit", allview.EditCustomer.as_view()),

]
urlpatterns += staticfiles_urlpatterns()
urlpatterns+=static(settings.IMAGE_URL,document_root=settings.IMAGE_ROOT)
