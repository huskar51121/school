from django.urls import path
from . import views

urlpatterns = [
    path('register', views.UserRegisterView.as_view(), name='user-list'),
    path('login', views.UserLoginView.as_view(), name='login'),
    path('module', views.ModuleView.as_view(), name='module'),
    path('rate', views.RateView.as_view(), name='rate'),
    path('average', views.CourseTeacherRateView.as_view(), name='average'),
]