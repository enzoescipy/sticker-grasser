from django.urls import path

from . import views

urlpatterns = [
    path('', views.List_testData.as_view()),
    path('<int:pk>/', views.Detail_testData.as_view()),
]