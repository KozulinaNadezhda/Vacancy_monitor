from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('vacancies/', views.vacancy_list, name='vacancy_list'),
]