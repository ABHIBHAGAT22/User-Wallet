from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    
path('', views.index),
    path('dash/', views.dash),

    path('register/',views.signup,name='signup'),
    path('otpverify1/',views.otpverify1),
    path('login/',views.signin),
    path('otpverify2/',views.otpverify2),
    path('addmoney/',views.addmoney),
    path('sendmoney/',views.sendmoney),
    path('history/',views.history),
    path('logout/',views.logout),
]

