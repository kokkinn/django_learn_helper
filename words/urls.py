from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.list_view, name="list_view"),
    path('add/', views.add_view),
    path('test/', views.test_view),
    path('', views.home_view),
    path('<uuid:uuid>/', views.one_word_view, name="single_word")
]
