from django.urls import path
from . import views

app_name = 'words'

urlpatterns = [
    path('list/', views.WordsListView.as_view(), name="list"),
    path('add/', views.add_view),
    path('test/', views.test_view),
    path('', views.home_view, name="home"),
    path('<uuid:uuid>/', views.one_word_view, name="single"),
    path("create/", views.WordCreateView.as_view(), name="create"),
    path("update/<uuid:uuid>/", views.WordUpdateView.as_view(), name="update"),
    path("delete/<uuid:uuid>/", views.delete_view, name="delete"),
    path("groups/", views.GroupsListView.as_view(), name="groups_list"),
    path("groups/<uuid:uuid>", views.words_in_group_list_view, name='group'),
    path("groups/create", views.GroupCreateView.as_view(), name="group_create"),
    path("groups/update/<uuid:uuid>", views.GroupUpdateView.as_view(), name="group_update")


]
