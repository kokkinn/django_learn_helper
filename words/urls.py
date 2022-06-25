from django.urls import path
from . import views

app_name = 'words'

urlpatterns = [
    path('list/', views.WordsListView.as_view(), name="list"),
    path('add/', views.add_view),
    path('test/', views.test_view),
    path('', views.home_view, name="home"),
    path('<uuid:uuid>/', views.one_word_view, name="single"),
    path("create_word/", views.create_word, name="create"),
    path("update_word/<uuid:uuid>/", views.update_word, name="update"),
    path("delete_word/<uuid:uuid>/", views.delete_view, name="delete"),
    path("groups/", views.groups_list_view, name="groups_list"),
    path("groups/<uuid:uuid>", views.words_in_group_list_view, name='group')


]
