from django.urls import path
from . import views

urlpatterns = [
    path('list/<str:pk>', views.list_view),
    path('add/', views.add_view),
    path('test/', views.test_view),
    path('', views.home_view),
]
